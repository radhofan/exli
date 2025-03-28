import collections
import glob
import os
import time
from typing import Dict, List, Set

import seutil as se
from exli.macros import Macros
from exli.reduce import reduce_suite
from exli.util import Util
from jsonargparse import CLI
from tqdm import tqdm
import re


class Eval:
    def replace_if(self, s: str):
        # remove if from the original code
        if s.startswith("if"):
            s = s[2:].strip()
        if s.endswith("{"):
            s = s[:-1].strip()
        if s.startswith("(") and s.endswith(")"):
            # remove () from the original code
            s = s[1:-1].strip()
        return s

    # python -m exli.eval run_tests_with_mutants --project_name Asana_java-asana
    # install inlinetest-internal/java
    def run_tests_with_mutants(
        self,
        project_name: str,
        sha: str,
        test_types: List[str] = None,
        mutator: str = Macros.universalmutator,
        log_path: str = None,
        seed: int = Macros.DEFAULT_SEED,
    ):
        """
        Apply each mutant to the project and run the inline tests to check if tests can kill the mutant.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            test_types (List[str], optional): The types of tests to run. Available options are ["r0", "r1", "dev", "randoop", "evosuite"]. Defaults to None. If None, all types of tests will be run.
            mutator (str, optional): The type of mutator. Available options are ["universalmutator", "major"]. Defaults to "universalmutator".
            log_path (str, optional): The path to save the log file. Defaults to None.
        """
        if mutator in [Macros.universalmutator, Macros.major]:
            mutants_file = Macros.mutants_dir / f"{project_name}-{sha}-{mutator}.json"
        else:
            raise Exception(f"Unknown mutant type: {mutator}")
        if not mutants_file.exists():
            print(f"no mutants for {project_name}")
            return

        eval_log = Macros.log_dir / "eval"
        if not eval_log.exists():
            se.bash.run(f"mkdir -p {eval_log}")
        temp_dir = Macros.log_dir / "eval" / "temp"
        if not temp_dir.exists():
            se.bash.run(f"mkdir -p {temp_dir}")

        Util.prepare_project(project_name, sha)

        # execute r0, r1 tests first to check if there is compilation failure
        if test_types is None:
            test_types = [
                Macros.r0,
                Macros.r1,
                Macros.dev,
                Macros.randoop,
                Macros.evosuite,
            ]
        for test_type in test_types:
            initial_num_failed_tests = 0
            if test_type in [Macros.dev, Macros.randoop, Macros.evosuite]:
                tests_log_file = f"{Macros.log_dir}/run-unit-tests/{project_name}-{sha}-{test_type}.log"
                if os.path.exists(tests_log_file):
                    os.remove(tests_log_file)
                Util.prepare_project(project_name, sha)
                self.run_tests(project_name, sha, test_type, seed, tests_log_file)
                initial_num_failed_tests = self.get_num_failed_tests(tests_log_file)
            mutants = se.io.load(mutants_file, se.io.Fmt.json)
            if not mutants:
                print(f"no mutants for {project_name}")
                return
            res = []
            updated_mutants = []
            for mutant in tqdm(mutants):
                if "compilation_failure" in mutant and mutant["compilation_failure"]:
                    continue
                original_code = mutant["orginal_code"].strip()
                mutated_code = mutant["mutated_code"].strip()
                file_path = mutant["filepath"]
                if not file_path.startswith(f"{Macros.home_dir}"):
                    file_path = re.sub(
                        r"/home/[^/]+/", f"{Macros.home_dir}/", file_path
                    )
                line_num = mutant["linenumber"]
                inline_test_name = (
                    file_path.split("/")[-1].split(".")[0] + f"_{line_num}Test.java"
                )
                mutant_res = {}
                mutant_res["id"] = mutant["id"]
                # add inline tests to the file
                Util.prepare_project(project_name, sha)
                with se.io.cd(Macros.downloads_dir / project_name):
                    if test_type in [Macros.dev, Macros.randoop, Macros.evosuite]:
                        # replace the original code with the mutated code
                        file_content = se.io.load(file_path, se.io.Fmt.txt)
                        lines = file_content.splitlines()
                        lines[line_num - 1] = mutated_code
                        se.io.dump(file_path, "\n".join(lines), se.io.Fmt.txt)
                    elif test_type in [Macros.r0, Macros.r1]:
                        inline_test_fqn = Util.get_full_class_name(file_path)
                        inline_test_path_with_package = (
                            inline_test_fqn.replace(".", "/") + ".java"
                        )
                        if test_type == Macros.r0:
                            file_path_with_inline_test = Macros.r0_tests_dir
                        elif test_type == Macros.r1:
                            file_path_with_inline_test = Macros.r1_tests_dir
                        else:
                            raise Exception(f"unknown test type: {test_type}")
                        file_path_with_inline_test = (
                            file_path_with_inline_test
                            / f"{project_name}-{sha}"
                            / inline_test_path_with_package
                        )
                        if not file_path_with_inline_test.exists():
                            print("file not exist", file_path_with_inline_test)
                            continue
                        file_path_with_inline_test_temp = (
                            temp_dir / inline_test_path_with_package
                        )
                        se.bash.run(
                            f"mkdir -p {os.path.dirname(file_path_with_inline_test_temp)}"
                        )
                        se.bash.run(
                            f"cp {file_path_with_inline_test} {file_path_with_inline_test_temp}"
                        )
                        file_content = se.io.load(
                            file_path_with_inline_test_temp, se.io.Fmt.txt
                        )

                        if original_code in file_content:
                            file_content = file_content.replace(
                                original_code, mutated_code
                            )
                            se.io.dump(
                                file_path_with_inline_test_temp,
                                file_content,
                                se.io.Fmt.txt,
                            )
                        else:
                            # replace the original code with the mutated code
                            # String buildNumber = matcher.group( 4 ) in the file content may be String buildNumber = matcher.group(4)
                            remove_space_original_code = original_code.replace(" ", "")
                            lines = file_content.splitlines()
                            replace = False
                            new_lines = []
                            for line in lines:
                                if line != "" and line.strip().replace(
                                    " ", ""
                                ).startswith(remove_space_original_code):
                                    new_line = (
                                        mutated_code
                                        + line.strip().replace(" ", "")[
                                            len(remove_space_original_code) :
                                        ]
                                    )
                                    new_lines.append(new_line)
                                    replace = True
                                else:
                                    new_lines.append(line)
                            if not replace:
                                error_message = f"cannot find {original_code} in {file_path_with_inline_test}"
                                print(error_message)
                                if log_path:
                                    se.io.dump(
                                        log_path,
                                        [error_message],
                                        se.io.Fmt.txtList,
                                        append=True,
                                    )
                                continue

                            se.io.dump(
                                file_path_with_inline_test_temp,
                                "\n".join(new_lines),
                                se.io.Fmt.txt,
                            )
                        if test_type == Macros.r0:
                            Util.parse_inline_tests(
                                project_name,
                                sha,
                                f"{Macros.r0_tests_dir}/{project_name}-{sha}",
                                f"{Macros.r0_its_dir}/{project_name}-{sha}",
                                file_path_with_inline_test_temp,
                            )
                        elif test_type == Macros.r1:
                            Util.parse_inline_tests(
                                project_name,
                                sha,
                                f"{Macros.r1_tests_dir}/{project_name}-{sha}",
                                f"{Macros.r1_its_dir}/{project_name}-{sha}",
                                file_path_with_inline_test_temp,
                            )
                        # clean the temp file
                        se.bash.run(f"rm {file_path_with_inline_test_temp}")
                    # add timeout when running tests
                    if test_type in [Macros.r0, Macros.r1]:
                        tests_log_file = (
                            eval_log
                            / f"{project_name}-{sha}-{test_type}-{inline_test_name}-{mutant['id']}-{mutator}.log"
                        )
                    else:
                        # no enough space to save all the log files, so Macros.dev, Macros.randoop, Macros.evosuite will share the same log file across different mutants
                        tests_log_file = (
                            eval_log / f"{project_name}-{sha}-{test_type}-{mutator}.log"
                        )
                    if tests_log_file.exists():
                        # remove the log file if it exists
                        se.bash.run(f"rm {tests_log_file}")
                    try:
                        with se.TimeUtils.time_limit(600):
                            end_time = -1
                            start_time = time.time()
                            deps_file = (
                                Macros.unit_tests_dir
                                / f"{project_name}-{sha}"
                                / "deps.txt"
                            )
                            if test_type == Macros.r0:
                                # run all inline tests
                                run_res, returncode = Util.run_inline_tests(
                                    project_name,
                                    sha,
                                    f"{Macros.r0_its_dir}/{project_name}-{sha}",
                                    f"{Macros.r0_tests_dir}/{project_name}-{sha}/{Macros.INLINE_GEN_DIR_NAME}",
                                    deps_file,
                                    inline_test_name,
                                )
                            elif test_type == Macros.r1:
                                # run inline tests
                                run_res, returncode = Util.run_inline_tests(
                                    project_name,
                                    sha,
                                    f"{Macros.r1_its_dir}/{project_name}-{sha}",
                                    f"{Macros.r0_tests_dir}/{project_name}-{sha}/{Macros.INLINE_GEN_DIR_NAME}",
                                    deps_file,
                                    inline_test_name,
                                )
                            elif test_type in [
                                Macros.dev,
                                Macros.randoop,
                                Macros.evosuite,
                            ]:
                                returncode = self.run_tests(
                                    project_name, sha, test_type, seed, tests_log_file
                                )
                            end_time = time.time()
                            if test_type == Macros.r0 or test_type == Macros.r1:
                                if run_res == "compilation failure":
                                    mutant["compilation_failure"] = True
                                else:
                                    mutant["compilation_failure"] = False
                                updated_mutants.append(mutant)
                                if mutant["compilation_failure"]:
                                    # The mutated code itself can be compiled successfully, but the inline test may not be compiled successfully. For example, the code is
                                    """
                                    int m (int a, int b){
                                        a = a >> 1; // original code
                                        a = b >> 1; // mutated code
                                        itest().given(a, 1).checkEq(a, 2); // inline test
                                        a += b;
                                        return a
                                    }
                                    """
                                    continue
                                se.io.dump(
                                    tests_log_file, run_res, se.io.Fmt.jsonPretty
                                )
                    except se.TimeoutException:
                        mutant_res[f"{test_type}-killed"] = False
                        mutant_res[f"{test_type}-time"] = 600
                        mutant_res["reason"] = "timeout"
                        res.append(mutant_res)
                        continue
                    except Exception as e:
                        print("error", e)
                        if end_time == -1:
                            end_time = time.time()
                        mutant_res[f"{test_type}-killed"] = False
                        mutant_res[f"{test_type}-time"] = end_time - start_time
                        mutant_res["reason"] = str(e)
                        res.append(mutant_res)
                        continue
                    if test_type in [Macros.r0, Macros.r1]:
                        if returncode == 0:
                            mutant_res[f"{test_type}-killed"] = False
                        else:
                            mutant_res[f"{test_type}-killed"] = True
                    else:
                        num_failed_tests = self.get_num_failed_tests(tests_log_file)
                        print(
                            "initial_num_failed_tests: ",
                            initial_num_failed_tests,
                            "num_failed_tests: ",
                            num_failed_tests,
                        )
                        if num_failed_tests > initial_num_failed_tests:
                            mutant_res[f"{test_type}-killed"] = True
                        else:
                            mutant_res[f"{test_type}-killed"] = False
                    mutant_res[f"{test_type}-time"] = end_time - start_time
                print("mutant_res", mutant_res)
                res.append(mutant_res)
            # save the results
            mutants_result_dir = Macros.results_dir / "mutants-eval-results"
            if not os.path.exists(mutants_result_dir):
                se.bash.run(f"mkdir -p {mutants_result_dir}")
            output_file = (
                mutants_result_dir / f"{project_name}-{sha}-{mutator}-{test_type}.json"
            )
            se.io.dump(
                output_file,
                res,
                se.io.Fmt.jsonPretty,
            )
            if test_type in [Macros.r0, Macros.r1]:
                se.io.dump(
                    mutants_file,
                    updated_mutants,
                    se.io.Fmt.jsonPretty,
                )

    def run_tests(
        self, project_name: str, sha: str, test_type: str, seed: int, log_file: str
    ):
        deps_file = Macros.unit_tests_dir / f"{project_name}-{sha}" / "deps.txt"
        if test_type == Macros.dev:
            # run unit tests
            returncode = Util.run_dev_written_unit_tests(project_name, log_file)
        elif test_type == Macros.randoop:
            # run randoop tests
            generated_tests_dir = (
                Macros.unit_tests_dir
                / f"{project_name}-{sha}"
                / f"{Macros.randoop}-tests-{seed}"
                / f"{Macros.randoop}-tests"
            )
            returncode = Util.run_randoop(project_name, generated_tests_dir, log_file)
        elif test_type == Macros.evosuite:
            # run evosuite tests
            generated_tests_dir = (
                Macros.unit_tests_dir
                / f"{project_name}-{sha}"
                / f"{Macros.evosuite}-tests-{seed}"
                / f"{Macros.evosuite}-tests"
            )
            returncode = Util.run_evosuite_command_line(
                project_name,
                generated_tests_dir,
                deps_file,
                log_file,
                600,
                False,
            )
        return returncode

    def get_num_failed_tests(self, log_path: str):
        """
        Get the number of failed tests from the log file.
        This is used to check if there are failed tests before applying the mutants.

        Args:
            log_path (str): The path to the log file.
        """
        num_failed_tests = 0
        if not os.path.exists(log_path):
            return num_failed_tests
        # get the number of failed tests
        log_content = se.io.load(log_path, se.io.Fmt.txt)
        # extract the number of tests from the log
        # surefire-style: Tests run: 6708, Failures: 0, Errors: 0, Skipped: 0
        # junit-cmd-style: OK (167 tests)
        # when there is failure: Tests run: 4619,  Failures: 2654
        # take the last one if there are multiple matches
        res = re.findall(r"Tests run: \d+, Failures: (\d+), Errors: (\d+)", log_content)
        if res:
            for match in res:
                failures, errors = map(int, match)
                num_failed_tests += failures + errors
        else:
            res = re.findall(r"Tests run: \d+,  Failures: (\d+)", log_content)
            for match in res:
                failures = int(match)
                num_failed_tests += failures
        return num_failed_tests

    # python -m exli.eval batch_run_tests_with_mutants
    def batch_run_tests_with_mutants(
        self,
        test_types: List[str] = None,
        mutator: str = Macros.universalmutator,
        test_project_name: str = None,
    ):
        """
        Batch process all projects to run tests after applying each mutant to source, and check if tests can kill the mutant.

        Args:
            test_types (List[str], optional): The types of tests to run. Available options are ["r0", "r1", "dev", "randoop", "evosuite"]. Defaults to None. If None, all types of tests will be run.
            mutator (str, optional): The type of mutator. Available options are ["universalmutator", "major"]. Defaults to "universalmutator".
            test_project_name (str, optional): The name of the project to be tested. If None, run tests for all projects. Defaults to None.
        """
        if test_types is None:
            test_types = [
                Macros.r0,
                Macros.r1,
                Macros.dev,
                Macros.randoop,
                Macros.evosuite,
            ]

        time_file = (
            Macros.results_dir / "time" / f"batch-run-tests-with-mutants-{mutator}.json"
        )
        if time_file.exists():
            res_dict = se.io.load(time_file, se.io.Fmt.json)
        else:
            res_dict = {}

        log_path = Macros.log_dir / "run-tests-with-mutants.log"
        if log_path.exists():
            se.bash.run(f"rm {log_path}")

        proj_sha_list = Util.get_project_names_list_with_sha()
        for project_name, sha in proj_sha_list:
            if test_project_name is not None and project_name != test_project_name:
                continue

            start_time = time.time()
            self.run_tests_with_mutants(
                project_name,
                sha,
                test_types,
                mutator,
                log_path,
            )
            end_time = time.time()
            res_dict[f"{project_name}-time"] = end_time - start_time

        se.io.dump(
            time_file,
            res_dict,
            se.io.Fmt.jsonPretty,
        )

    def batch_get_r2_tests(
        self,
        mutator: str = Macros.universalmutator,
        algo: str = Macros.greedy,
        test_project_name: str = None,
    ):
        """
        Batch process all projects to get the r2 tests.

        Args:
            mutator (str, optional): The tool used to generate mutants. Defaults to Macros.universalmutator.
            algo (str, optional): The algorithm used to minimize the tests. Defaults to Macros.greedy.
            test_project_name (str, optional): The name of the project to be tested. Defaults to None.
        """
        for project_name, sha in Util.get_project_names_list_with_sha():
            if test_project_name is not None and project_name != test_project_name:
                continue
            output_path = (
                Macros.results_dir
                / Macros.r2
                / f"{project_name}-{sha}-{mutator}-{algo}.txt"
            )
            self.get_r2_tests(project_name, sha, mutator, algo, output_path)

        if test_project_name is None:
            # since we use greedy algorithm results in the paper, we combine the results of greedy algorithm into Macros.results/r2-universalmutator-greedy-passed-tests.txt
            r2_tests_path = (
                Macros.results_dir / f"{Macros.r2_um}-{Macros.greedy}-passed-tests.txt"
            )
            r2_tests = []
            for project_name, sha in Util.get_project_names_list_with_sha():
                if test_project_name is not None and project_name != test_project_name:
                    continue
                r2_tests_path_project = (
                    Macros.results_dir
                    / Macros.r2
                    / f"{project_name}-{sha}-{mutator}-{algo}.txt"
                )
                if r2_tests_path_project.exists():
                    r2_tests.extend(
                        se.io.load(r2_tests_path_project, se.io.Fmt.txtList)
                    )
            se.io.dump(r2_tests_path, r2_tests, se.io.Fmt.txtList)

    def get_r2_tests(
        self,
        project_name: str,
        sha: str,
        mutator: str,
        algo: str,
        output_path: str = None,
    ):
        """
        Get the r2 tests.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            mutator (str): The type of mutator.
            algo (str): The algorithm used to minimize the tests.
            output_path (str): The path to save the results.
        """
        self.test_to_killed_mutants(project_name, sha, mutator, Macros.r0)
        self.test_to_killed_mutants(project_name, sha, mutator, Macros.r1)
        self.add_back_itests_kill_mutants(project_name, sha, mutator)
        self.minimize_tests(project_name, sha, mutator)
        self.add_back_itests_without_mutants(project_name, sha, mutator)

        formatted_minimized_tests = []
        minimized_tests_path = (
            Macros.results_dir
            / "minimized"
            / f"{project_name}-{sha}-{mutator}-{algo}.txt"
        )
        if minimized_tests_path.exists():
            minimized_tests = se.io.load(minimized_tests_path, se.io.Fmt.txtList)
            for minimized_test in minimized_tests:
                # mojohaus_properties-maven-plugin#org.codehaus.mojo.properties.ReadPropertiesMojo_382Test#testLine305()#r1
                project_name, fqn_with_lineno, test_name, test_source = (
                    minimized_test.split("#")
                )
                m = re.match(r"(.+)_(\d+)Test", fqn_with_lineno)
                fqn, target_stmt_lineno = m.group(1), m.group(2)
                itest_lineno = re.match(r"testLine(\d+)\(\)", test_name).group(1)
                formatted_minimized_tests.append(
                    f"{project_name};{fqn};{target_stmt_lineno};{itest_lineno};{test_source}"
                )

        itests_without_mutants = []
        for f in (Macros.results_dir / "itests-without-mutants").glob(
            f"{project_name}-{sha}-{mutator}.txt"
        ):
            itests_without_mutants.extend(se.io.load(f, se.io.Fmt.txtList))
        # format by adding test_source
        itests_without_mutants = [
            itest + ";" + Macros.r1 for itest in itests_without_mutants
        ]

        r2_tests = []
        r2_tests.extend(formatted_minimized_tests)
        r2_tests.extend(itests_without_mutants)
        if output_path is None:
            output_path = f"{Macros.results_dir}/{Macros.r2}/{project_name}-{sha}-{mutator}-{algo}.txt"
        se.io.dump(output_path, r2_tests, se.io.Fmt.txtList)

    # python -m exli.eval batch_test_to_killed_mutants --mutator "universalmutator"
    def batch_test_to_killed_mutants(
        self, mutator: str = Macros.universalmutator, test_project_name: str = None
    ):
        """
        Batch process all projects to get the killed mutants for each test.

        Args:
            mutator (str, optional): The tool used to generate mutants. Defaults to "universalmutator".
            test_project_name (str, optional): The name of the project to be tested. If None, collect the mapping from test to killed mutants for all projects. Defaults to None.
        """
        for project_name, sha in Util.get_project_names_list_with_sha():
            if test_project_name is not None and project_name != test_project_name:
                continue
            self.test_to_killed_mutants(project_name, sha, mutator, Macros.r0)
            self.test_to_killed_mutants(project_name, sha, mutator, Macros.r1)

    # python -m exli.eval test_to_killed_mutants
    # --test_type "r1"
    def test_to_killed_mutants(
        self,
        project_name: str,
        sha: str,
        mutator: str = Macros.universalmutator,
        test_type: str = Macros.r0,
    ):
        """
        Get the killed mutants for each test.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            mutator (str, optional): The type of mutator. Available options are ["universalmutator", "major"]. Defaults to "universalmutator".
            test_type (str, optional): The type of tests to run. Available options are ["r0", "r1"]. Defaults to "r0".
        """
        killed_mutants_file = (
            Macros.results_dir
            / "killed-mutants"
            / f"{project_name}-{sha}-{mutator}-{test_type}.json"
        )

        killed_mutants_res = []

        if mutator in [Macros.universalmutator, Macros.major]:
            mutants_file = Macros.mutants_dir / f"{project_name}-{sha}-{mutator}.json"
        else:
            raise Exception("unknown mutant type")

        if not mutants_file.exists():
            return
        mutants = se.io.load(mutants_file, se.io.Fmt.json)
        for mutant in mutants:
            if "compilation_failure" in mutant and mutant["compilation_failure"]:
                continue
            # log/eval/AquaticInformatics_aquarius-sdk-java-8f4edb9-all-AquariusServerVersion_19Test.java-0-{mutator}.log
            index = mutant["id"]
            filepath = mutant["filepath"]
            linenumber = mutant["linenumber"]
            test_name = (
                filepath.split("/")[-1].replace(".java", "") + f"_{linenumber}Test.java"
            )
            mutation_res_file = (
                Macros.log_dir
                / "eval"
                / f"{project_name}-{sha}-{test_type}-{test_name}-{index}-{mutator}.log"
            )
            if not mutation_res_file.exists():
                print(f"file not exist: {mutation_res_file}")
                continue
            report = se.io.load(mutation_res_file, se.io.Fmt.json)
            if report is None or "testcase" not in report["testsuite"]:
                print(f"{mutation_res_file} is null")
                continue
            test_cases = report["testsuite"]["testcase"]
            if not isinstance(test_cases, list):
                test_cases = [test_cases]
            for test_case in test_cases:
                if "failure" in test_case or "error" in test_case:
                    target_stmt_linenumber = (
                        test_case["@classname"]
                        .split(".")[-1]
                        .split("_")[-1]
                        .replace("Test", "")
                    )
                    inline_test_linenumber = (
                        test_case["@name"].replace("testLine", "").replace("()", "")
                    )
                    killed_mutants_item = {
                        "test_class_name": test_case["@classname"],
                        "test_method_name": test_case["@name"],
                        "target_stmt_linenumber": target_stmt_linenumber,
                        "inline_test_linenumber": inline_test_linenumber,
                        "id": index,
                        "killed_mutant_file_path": filepath,
                    }
                    killed_mutants_res.append(killed_mutants_item)

        se.io.dump(
            killed_mutants_file,
            killed_mutants_res,
            se.io.Fmt.jsonPretty,
        )

    def get_test_to_killed_mutants(
        self,
        project_name: str,
        sha: str,
        mutator: str,
        test_type: str,
    ):
        test_to_killed_mutants_dict = collections.defaultdict(set)
        killed_mutants_file = (
            Macros.results_dir
            / "killed-mutants"
            / f"{project_name}-{sha}-{mutator}-{test_type}.json"
        )
        if not killed_mutants_file.exists():
            return test_to_killed_mutants_dict
        killed_mutants = se.io.load(killed_mutants_file, se.io.Fmt.json)
        for killed_mutant in killed_mutants:
            test_class_name = killed_mutant["test_class_name"]
            test_method_name = killed_mutant["test_method_name"]
            mutant_index = killed_mutant["id"]
            test_to_killed_mutants_dict[
                project_name + "#" + test_class_name + "#" + test_method_name
            ].add(f"{project_name}-{mutant_index}")
        return test_to_killed_mutants_dict

    # python -m exli.eval add_back_tests
    def add_back_itests_kill_mutants(
        self, project_name: str, sha: str, mutator: str = Macros.universalmutator
    ):
        """
        Add back tests in r0 that can kill mutants not killed by tests in r1.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            mutator (str, optional): The type of mutator. Defaults to "universalmutator".
        """
        # collect the mutants that are killed by r0
        killed_mutant_to_tests_dict = collections.defaultdict(set)
        killed_mutants_file = (
            Macros.results_dir
            / "killed-mutants"
            / f"{project_name}-{sha}-{mutator}-{Macros.r0}.json"
        )

        if not killed_mutants_file.exists():
            return []
        killed_mutants = se.io.load(killed_mutants_file, se.io.Fmt.json)
        for killed_mutant in killed_mutants:
            test_class_name = killed_mutant["test_class_name"]
            test_method_name = killed_mutant["test_method_name"]
            mutant_index = killed_mutant["id"]
            killed_mutant_to_tests_dict[mutant_index].add(
                project_name + "#" + test_class_name + "#" + test_method_name
            )

        # load the mutantion results of r1
        if mutator in [Macros.universalmutator, Macros.major]:
            r1_mutants_result_file = (
                Macros.results_dir
                / "mutants-eval-results"
                / f"{project_name}-{sha}-{mutator}-{Macros.r1}.json"
            )
        else:
            raise Exception("Invalid mutant type")

        if not r1_mutants_result_file.exists():
            return []
        r1_mutants_result = se.io.load(r1_mutants_result_file, se.io.Fmt.json)

        # for each mutant that is not killed by r1, add back the r0 tests that can kill the mutant
        mutants_to_add_back_tests = collections.defaultdict(set)
        for mutated_result in r1_mutants_result:
            index = mutated_result["id"]
            if mutated_result[f"{Macros.r1}-killed"]:
                continue
            else:
                if index in killed_mutant_to_tests_dict:
                    # this mutant is not killed by r1 tests but killed by r0 tests
                    # add back the test that can kill the mutant
                    mutants_to_add_back_tests[f"{project_name}-{index}"].update(
                        killed_mutant_to_tests_dict[index]
                    )

        # all mutants to add back tests -> test to killed mutants
        addback_t2m = collections.defaultdict(set)
        for mutant, tests in mutants_to_add_back_tests.items():
            for test in tests:
                addback_t2m[test].add(mutant)
        # dump the results
        se.io.dump(
            Macros.results_dir
            / "killed-mutants"
            / "add-back-tests-to-killed-mutants"
            / f"{project_name}-{sha}-{mutator}.txt",
            [
                test + "," + ",".join(sorted(mutants))
                for test, mutants in addback_t2m.items()
            ],
            se.io.Fmt.txtList,
        )

        # merge with r1 tests
        r1_t2m = self.get_test_to_killed_mutants(project_name, sha, mutator, Macros.r1)
        merged_t2m = collections.defaultdict(set)
        for test, mutants in r1_t2m.items():
            merged_t2m[test + "#" + Macros.r1].update(mutants)
        for test, mutants in addback_t2m.items():
            merged_t2m[test + "#" + Macros.r0].update(mutants)
        se.io.dump(
            Macros.results_dir
            / "killed-mutants"
            / "merged-tests-to-killed-mutants"
            / f"{project_name}-{sha}-{mutator}.txt",
            [
                test + "," + ",".join(sorted(mutants))
                for test, mutants in merged_t2m.items()
            ],
            se.io.Fmt.txtList,
        )

    # python -m exli.eval minimize_tests
    def minimize_tests(
        self, project_name: str, sha: str, mutator: str = Macros.universalmutator
    ):
        """
        Minimize the tests that can kill the mutants.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            mutator (str, optional): The type of mutator. Defaults to "universalmutator".
        """
        data_file = (
            Macros.results_dir
            / "killed-mutants"
            / "merged-tests-to-killed-mutants"
            / f"{project_name}-{sha}-{mutator}.txt"
        )

        for algorithm in Macros.test_minimization_algorithms:
            out_file = (
                Macros.results_dir
                / "minimized"
                / f"{project_name}-{sha}-{mutator}-{algorithm}.txt"
            )
            self.minimize_tests_helper(algorithm, data_file, out_file, project_name)

    def minimize_tests_helper(self, algorithm: str, data_file: str, out_file: str):
        if not data_file.exists():
            print(f"{data_file} does not exist")
            return

        if not out_file.parent.exists():
            se.bash.run(f"mkdir -p {out_file.parent}")

        orig_file = se.io.mktmp("exli")
        se.bash.run(f"cut -d, -f1 '{data_file}' > '{orig_file}'", 0)
        # run test minimization scripts
        reduce_suite(
            data_file=data_file,
            orig_file=orig_file,
            algorithm=algorithm,
            out=out_file,
            tiebreak_map={},  # no tiebreak
        )
        # sort results
        selected_tests = se.io.load(out_file, se.io.Fmt.txtList)
        se.io.dump(out_file, sorted(selected_tests), se.io.Fmt.txtList)
        se.io.rm(orig_file)

    def batch_minimize_tests(
        self, test_project_name: str = None, mutator: str = Macros.universalmutator
    ):
        """
        Batch process all projects to minimize the tests that can kill the mutants.

        Args:
            test_project_name (str, optional): The name of the project to be tested. If None, minimize tests for all projects. Defaults to None.
            mutator (str, optional): The type of mutator. Defaults to "universalmutator".
        """
        for project_name, sha in Util.get_project_names_list_with_sha():
            if test_project_name is not None and project_name != test_project_name:
                continue
            self.minimize_tests(project_name, sha, mutator)

    def add_back_itests_without_mutants(
        self, project_name: str, sha: str, mutator: str
    ):
        """
        Add back the inline tests
        1. whose target statements are not mutated.
        2. whose target statements are mutated but no tests can kill the mutants.

        Args:
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
            mutator (str): The type of mutator.
        """
        # format of r1-passed-tests.txt
        # mp911de_logstash-gelf;biz.paluch.logging.gelf.wildfly.WildFlyJsonFormatter;119;120
        target_stmt_to_inline_tests = Util.get_target_stmt_to_inline_tests(
            Macros.results_dir / f"{Macros.r1}-passed-tests.txt"
        )
        mutated_target_stmts = set()

        for test_type in [Macros.r0, Macros.r1]:
            if mutator in [Macros.universalmutator, Macros.major]:
                killed_mutant_file = (
                    Macros.results_dir
                    / "killed-mutants"
                    / f"{project_name}-{sha}-{mutator}-{test_type}.json"
                )
            else:
                raise Exception("unknown mutant type")

            if killed_mutant_file.exists():
                mutated_results = se.io.load(killed_mutant_file)
                for mutated_res in mutated_results:
                    # "test_class_name": "com.asana.resources.gen.PortfoliosBase_214Test"
                    classname = mutated_res["test_class_name"].split("_")[0]
                    mutated_target_stmt = f"{project_name};{classname};{mutated_res['target_stmt_linenumber']}"
                    mutated_target_stmts.add(mutated_target_stmt)

        print(f"{len(mutated_target_stmts)=}")
        not_mutated_inline_tests = set()
        for target_stmt, inline_tests in target_stmt_to_inline_tests.items():
            current_proj_name = target_stmt.split(";")[0]
            if current_proj_name != project_name:
                continue
            if target_stmt not in mutated_target_stmts:
                not_mutated_inline_tests.update(inline_tests)
        output_path = (
            Macros.results_dir
            / "itests-without-mutants"
            / f"{project_name}-{sha}-{mutator}.txt"
        )
        se.io.dump(output_path, not_mutated_inline_tests, se.io.Fmt.txtList)

    # python -m exli.eval save_r2_inline_test_no_source_code
    def save_r2_inline_test_no_source_code(
        self, mutator: str = Macros.universalmutator
    ):
        not_mutated_inline_tests = se.io.load(
            Macros.results_dir / f"not-mutated-inline-tests-{mutator}.txt",
            se.io.Fmt.txtList,
        )
        updated_not_mutated_inline_tests = []
        # format tests in not_mutated_inline_tests
        # from wmixvideo_nfe;com.fincatto.documentofiscal.validadores.DFStringValidador;823;874
        # to Asana_java-asana#com.asana.resources.ProjectStatuses_24Test#testLine28()
        for not_mutated_inline_test in not_mutated_inline_tests:
            (
                project_name,
                classname,
                target_line,
                inline_test_line,
            ) = not_mutated_inline_test.split(";")
            updated_not_mutated_inline_test = f"{project_name}#{classname}_{target_line}Test#testLine{inline_test_line}()"
            updated_not_mutated_inline_tests.append(updated_not_mutated_inline_test)
        for algorithm in Macros.test_minimization_algorithms:
            minimized_file = (
                Macros.results_dir / "minimized" / f"{algorithm}-{mutator}.txt"
            )
            minimized_tests = se.io.load(minimized_file, se.io.Fmt.txtList)
            r2_inline_tests = []
            r2_inline_tests.extend(minimized_tests)
            r2_inline_tests.extend(updated_not_mutated_inline_tests)
            se.io.dump(
                Macros.results_dir / Macros.r2 / f"{algorithm}-{mutator}.txt",
                sorted(r2_inline_tests),
                se.io.Fmt.txtList,
            )

    def line_number_to_test(self, test_type: str, project_name: str, sha: str):
        """
        Find the line number to test mapping for the inline tests.

        Args:
            test_type (str): The type of tests. Available options are ["r0", "r1"].
            project_name (str): The name of the project.
            sha (str): The commit sha of the project.
        """
        if sha is None:
            sha = Util.get_sha(project_name)

        with se.io.cd(Macros.downloads_dir / project_name):
            se.bash.run("git clean -xfd")
            se.bash.run("git checkout .")
            se.bash.run(f"git checkout {sha}")
        line_no_to_test = dict()
        if test_type == Macros.r1:
            source_code_dir_path = Macros.r1_tests_dir / f"{project_name}-{sha}"
        elif test_type == Macros.r0:
            source_code_dir_path = Macros.r0_tests_dir / f"{project_name}-{sha}"
        else:
            raise Exception(f"invalid test type: {test_type}")
        java_files = glob.glob(
            f"{source_code_dir_path}" + "/**/*.java",
            recursive=True,
        )
        for java_file in java_files:
            classlastname = java_file.replace(".java", "").split("/")[-1]
            java_file_content = se.io.load(java_file, se.io.Fmt.txtList)
            line_index = 0
            while line_index < len(java_file_content):
                line = java_file_content[line_index]
                if line.strip().startswith("package"):
                    package_name = line.strip().replace(";", "").split(" ")[1].strip()
                    classname = f"{package_name}.{classlastname}"
                elif line.strip().startswith("itest("):
                    line_no = line_index + 1
                    inline_test_code = line.strip()
                    while not line.strip().endswith(";"):
                        line_index += 1
                        line = java_file_content[line_index]
                        inline_test_code += line.strip()
                    # /home/user/exli/_downloads/wmixvideo_nfe/src/main/java/com/fincatto/documentofiscal/validadores/DFBigDecimalValidador.java;83;new Here("Dev", 83).given(tamanho,7).given(valor,"50.xml").given(posicaoPontoFlutuante,2).checkFalse(group());
                    target_stmt_line_no = (
                        inline_test_code.split(")")[0].split(",")[-1].strip()
                    )
                    # find the java file path with class name
                    filepaths = glob.glob(
                        f"{Macros.downloads_dir}/{project_name}"
                        + f"/**/{classname.replace(r'.', r'/')}.java",
                        recursive=True,
                    )
                    if len(filepaths) != 1:
                        print(filepaths)
                        raise Exception(
                            f"cannot find the file path for {classlastname}"
                        )
                    line_no_to_test[classname + "#" + str(line_no)] = (
                        filepaths[0]
                        + ";"
                        + target_stmt_line_no
                        + ";"
                        + inline_test_code
                    )
                line_index += 1
        return line_no_to_test

    # python -m exli.eval batch_parse_log_file
    def batch_parse_log_file(self):
        """parse the log file to get the inline"""
        log_path = Macros.log_dir / "parse-log.log"
        for input_type in ["merged"] + Macros.test_minimization_algorithms:
            generated_tests_dir = Macros.project_dir / f"{input_type}-tests"
            se.io.mkdir(generated_tests_dir, fresh=True)

            for project_name, sha in Util.get_project_names_list_with_sha():
                inline_test_log_path = f"{Macros.r1_tests_dir}/{project_name}-{sha}/inlinetest-log-{input_type}.txt"
                if not os.path.exists(inline_test_log_path):
                    continue

                proj_generated_tests_dir = f"{generated_tests_dir}/{project_name}-{sha}"
                # create the directory if not exist
                if not os.path.exists(proj_generated_tests_dir):
                    os.makedirs(proj_generated_tests_dir)

                Util.parse_log(
                    project_name,
                    sha,
                    inline_test_log_path,
                    proj_generated_tests_dir,
                    log_path,
                )

    # python -m exli.eval check_num_of_inline_tests
    def check_num_of_inline_tests(self):
        for input_type in ["merged"] + Macros.test_minimization_algorithms:
            for project_name, commit in Util.get_project_names_list_with_sha():
                INLINE_TEST_LOG_FILE_PATH = f"{Macros.r1_tests_dir}/{project_name}-{commit}/inlinetest-log-{input_type}.txt"
                if not os.path.exists(INLINE_TEST_LOG_FILE_PATH):
                    continue
                inline_tests = se.io.load(INLINE_TEST_LOG_FILE_PATH, se.io.Fmt.txtList)
                logged_inline_test = len(
                    [inline_test for inline_test in inline_tests if inline_test]
                )
                sha = Util.get_sha(project_name)
                added_inline_test = se.bash.run(
                    f"grep -rn 'itest(' {Macros.project_dir}/{input_type}-tests/{project_name}-{sha}/* | wc -l"
                ).stdout
                if logged_inline_test != int(added_inline_test):
                    print(
                        input_type, project_name, logged_inline_test, added_inline_test
                    )

    # python -m exli.eval check_set_of_reduction_results
    def check_set_of_reduction_results(self):
        """
        Compare the number of reduced tests for different test reduction algorithms. Used for sanity check.
        """
        algo_to_tests = collections.defaultdict(list)
        new_algo_to_tests = collections.defaultdict(list)
        for algorithm in Macros.test_minimization_algorithms:
            file_path = (
                Macros.results_dir / "minimized" / f"{algorithm}-minimized-all.txt"
            )
            tests = se.io.load(file_path, se.io.Fmt.txtList)
            algo_to_tests[algorithm].extend(tests)

            new_file_path = (
                Macros.results_dir / "minimized-o" / f"{algorithm}-minimized-all.txt"
            )
            new_tests = se.io.load(new_file_path, se.io.Fmt.txtList)
            new_algo_to_tests[algorithm].extend(new_tests)
        # check if the list of tests are the same
        for algo1, tests1 in algo_to_tests.items():
            for algo2, tests2 in algo_to_tests.items():
                if algo1 == algo2:
                    continue
                if set(tests1) != set(tests2):
                    # find the difference
                    diff = set(tests1) - set(tests2)
                    print(algo1, algo2, len(diff))
            new_tests = new_algo_to_tests[algo1]
            if set(tests1) != set(new_tests):
                # find the difference
                diff = set(tests1) - set(new_tests)
                print(algo1, "new", len(diff))

    def get_failed_tests(self, test_type: str = Macros.r0):
        """
        Get failed tests. This is used only when we saved the initial
        r0-tests and r1-tests (if we did not execute `python -m
        exli.main remove_failed_tests`)

        Args:
            test_type (str, optional): Inline tests type. Defaults to
            Macros.r0.
        """
        all_pass_test_file = Macros.results_dir / f"{test_type}-passed-tests.txt"
        java_files_root_dir = Macros.results_dir / f"{test_type}-tests"

        all_proj_to_stmts, _ = Util.get_projs_to_stmts_and_inline_tests(
            all_pass_test_file
        )
        total_excluded_inline_tests = 0
        total_kept_inline_tests = 0
        for project_name, sha in Util.get_project_names_list_with_sha():
            excluded_inline_tests = 0
            passed_stmts = all_proj_to_stmts[project_name]
            java_files_dir = java_files_root_dir / f"{project_name}-{sha}"
            if not os.path.exists(java_files_dir):
                print(f"java files dir not exist: {java_files_dir}")
                continue
            java_files = glob.glob(f"{java_files_dir}/**/*.java", recursive=True)
            for java_file in java_files:
                file_kept_inline_tests = 0
                newlines = []
                java_file_content = se.io.load(java_file, se.io.Fmt.txtList)
                index = 0
                while index < len(java_file_content):
                    line = java_file_content[index]
                    if line.strip().startswith("itest("):
                        while not java_file_content[index].strip().endswith(";"):
                            index += 1
                        # target stmt line no
                        classlastname = (
                            java_file.replace(".java", "").split("/")[-1].strip()
                        )
                        target_stmt_line_no = (
                            line.strip()
                            .split("itest(")[1]
                            .split(")")[0]
                            .split(",")[1]
                            .strip()
                        )
                        key = f".{classlastname}:{target_stmt_line_no}"
                        find_target_stmt = False
                        for passed_stmt in passed_stmts:
                            if passed_stmt.endswith(key):
                                find_target_stmt = True
                                break

                        if not find_target_stmt:
                            excluded_inline_tests += 1
                            print(project_name, java_file, target_stmt_line_no, line)
                            index += 1
                            continue
                        else:
                            file_kept_inline_tests += 1
                            total_kept_inline_tests += 1
                    newlines.append(line)
                    index += 1
            total_excluded_inline_tests += excluded_inline_tests
            print(f"{project_name} excluded inline tests: {excluded_inline_tests}")
        print(f"total excluded inline tests: {total_excluded_inline_tests}")
        print(f"total kept inline tests: {total_kept_inline_tests}")

    # python -m exli.eval check_covered_stmts
    def check_covered_stmts(self):
        # load all target statements
        examples = se.io.load(Macros.results_dir / "target-statements.json")
        # get target statements that are covered by at least one unit test
        examples = [
            example
            for example in examples
            if example[f"{Macros.evosuite}_stmt_covered"] == True
            or example[f"{Macros.randoop}_stmt_covered"] == True
            or example[f"{Macros.dev}_stmt_covered"] == True
        ]
        covered_stmts = set()
        for example in examples:
            class_name = Util.file_path_to_class_name(example["filename"])
            covered_stmts.add(
                example["project"]
                + ";"
                + class_name
                + ";"
                + str(example["line_number"])
            )

        # target stmts from passing tests
        pass_test_file = Macros.results_dir / f"{Macros.r0}-passed-tests.txt"
        pass_tests = se.io.load(pass_test_file, se.io.Fmt.txtList)
        target_stmts = set()
        for test in pass_tests:
            project_name, classname, target_stmt_lineno, _ = test.split(";")
            target_stmts.add(f"{project_name};{classname};{target_stmt_lineno}")

        # compare the two sets
        print(f"covered stmts: {len(covered_stmts)}")
        print(f"passing tests target stmts: {len(target_stmts)}")
        print(
            f"covered stmts - passing tests target stmts: {len(covered_stmts - target_stmts)}"
        )
        print(
            f"passing tests target stmts - covered stmts: {target_stmts - covered_stmts}"
        )


if __name__ == "__main__":
    se.log.setup(Macros.log_file)
    CLI(Eval, as_positional=False)
