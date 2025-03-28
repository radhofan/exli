### NOTE: THIS REPOSITORY IS A REPRODUCIBLE PAPER EXPERIMENT AND IS INTENDED TO BE RAN INSIDE CHAMELEON TROVI
#### Reproduce this experiment via reproduce.ipynb
#### This experiment has been modified to ensure perfect replication
#### Reproduce this repository in Chameleon Trovi here: https://www.chameleoncloud.org/experiment/share/554b286d-5866-49da-9d36-9ce59b086cfe
#### Original repository link: https://github.com/SEED-VT/Web-Ads-Accessibility

# ExLi
Automatically extracting inline tests from unit tests and executing these inline tests with [itest][itest-url].

## Introduction
This repo contains the code and data for producing the experiments in [ExLi][paper-url].

### Inline test format
1. "Declare" part
`itest`

In our experiments, we use `itest(test_source, target_stmt_line_number)`, to represent the test source and the line number of the target statement in original file (note that after adding inline tests to the original file, the line numbers of target statements change).
For example, `itest("randoop", 57)` means that the test source is Randoop generated tests, and the target statement starts at line 57 in the original file.

2. "Assign" part
`given(var, value)`

3. "Assert" part
`assert(var, value)`

### Repo structure

#### Code
raninline: This directory constains the source code of TargetStmtFinder, VariablesFinder,
Instrumenter, Collector, Round1Reducer, and InlineTestConstructor.

python: This directory contains the scripts of running ExLi end-to-end and generates figures.

## How to use ExLi

### Requirements
- Docker
- Disk space: 10GB

In the docker, the following tools/dependencies are installed:
- Conda latest version
- Python 3.9 (or later)
- Java 8, JUnit 4
- Maven 3.8.3 (or later)

### Install
Build a docker image

`docker build -t exli .`

`docker run -it exli /bin/bash`


In the docker, create a Python environment named `exli`

`cd exli/python && bash prepare-conda-env.sh`

`conda activate exli`


### Usage

- For each command, append `--help` to see the usage and options.
> For example, `python -m exli.main find_target_stmts --help`
>
```txt
usage: main.py [options] find_target_stmts [-h] [--config CONFIG] [--print_config[=flags]]
                                           --project_name PROJECT_NAME --sha SHA
                                           --target_stmts_path TARGET_STMTS_PATH

Find target statements for a project.

  ...
  --project_name PROJECT_NAME
                        org_repo, e.g., https://github.com/Bernardo-MG/velocity-config-tool, the project name is
                        Bernardo-MG_velocity-config-tool (required, type: str)
  --sha SHA             commit hash (required, type: str)
  --target_stmts_path TARGET_STMTS_PATH
                        path to store the target statements (required, type: str)
```

- For each command, the argument and value can be seperated by `=` or space. For example, `--project_name=Bernardo-MG_velocity-config-tool` or `--project_name Bernardo-MG_velocity-config-tool` are both valid.
- To run on a specific project, replace `Bernardo-MG_velocity-config-tool` with the project name and `26226f5` with the commit hash. Notice that only projects that are in evaluated projects can be run with the command that only require `test_project_name`.

#### Step 1: Find the target statements

It will help EvoSuite reduce the search scope. Otherwise, EvoSuite will generate tests on the whole project, which may take a long time (~2 min * number of classes). Also, the second round reducer will generate mutants for these target statements.

In `exli/python` directory

```bash
python -m exli.main find_target_stmts --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --target_stmts_path=${HOME}/exli/results/target-stmt/Bernardo-MG_velocity-config-tool-26226f5.txt
```
> The generated target statements are in `${HOME}/exli/results/target-stmt/Bernardo-MG_velocity-config-tool-26226f5.txt`

> Alternatively, to use the default output file path
`python -m exli.main batch_find_target_stmts --test_project_name=Bernardo-MG_velocity-config-tool`

There are three target statements found in the project `Bernardo-MG_velocity-config-tool` at commit `26226f5`:

```txt
target stmt string;/home/itdocker/exli/_downloads/Bernardo-MG_velocity-config-tool/src/main/java/com/bernardomg/velocity/tool/ConfigTool.java;195;null;;null
target stmt string;/home/itdocker/exli/_downloads/Bernardo-MG_velocity-config-tool/src/main/java/com/bernardomg/velocity/tool/ConfigTool.java;200;null;;null
target stmt string;/home/itdocker/exli/_downloads/Bernardo-MG_velocity-config-tool/src/main/java/com/bernardomg/velocity/tool/ConfigTool.java;288;null;;null
```

#### Step 2: Generate unit tests and inline tests

In `exli/python` directory

```bash
python -m exli.main run --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --randoop=True --randoop_tl=100 --dev=True --evosuite=True --evosuite_tl=120 --seed=42 --log_path=${HOME}/exli/log/raninline.log
```

> The generated inline tests are in `${HOME}/exli/all-tests/Bernardo-MG_velocity-config-tool-26226f5`

> Alternatively, to use the default setting for test generation and output dirs path
`python -m exli.main batch_run --test_project_name=Bernardo-MG_velocity-config-tool`

#### Step 3: Execute the generated inline tests

In `exli/python` directory

Execute r0 inline tests:

```bash
python -m exli.main run_inline_tests --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --generated_tests_dir=${HOME}/exli/r0-tests/Bernardo-MG_velocity-config-tool-26226f5 --inline_tests_dir=${HOME}/exli/r0-its/Bernardo-MG_velocity-config-tool-26226f5 --inlinetest_report_path=${HOME}/exli/results/r0-its-report/Bernardo-MG_velocity-config-tool-26226f5.json --cached_objects_dir=${HOME}/exli/r0-tests/Bernardo-MG_velocity-config-tool-26226f5/.inlinegen --deps_file=${HOME}/exli/generated-tests/Bernardo-MG_velocity-config-tool-26226f5/deps.txt --parse_inline_tests=True --log_path=${HOME}/exli/log/run-its.log
```

Execute r1 inline tests:

```bash
python -m exli.main run_inline_tests --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --generated_tests_dir=${HOME}/exli/r1-tests/Bernardo-MG_velocity-config-tool-26226f5 --inline_tests_dir=${HOME}/exli/r1-its/Bernardo-MG_velocity-config-tool-26226f5 --inlinetest_report_path=${HOME}/exli/results/r1-its-report/Bernardo-MG_velocity-config-tool-26226f5.json --cached_objects_dir=${HOME}/exli/r0-tests/Bernardo-MG_velocity-config-tool-26226f5/.inlinegen --deps_file=${HOME}/exli/generated-tests/Bernardo-MG_velocity-config-tool-26226f5/deps.txt --parse_inline_tests=True --log_path=${HOME}/exli/log/run-its.log
```

> These two commands run the inline tests and generate the execution report at `${HOME}/exli/results/r1-its-report/Bernardo-MG_velocity-config-tool-26226f5.json` and `${HOME}/exli/results/r0-its-report/Bernardo-MG_velocity-config-tool-26226f5.json`
>
> `r1-tests` and `r0-tests` store the source code with inline tests, `r1-its` and `r0-its` store the inline tests parsed by itest framework
> 
> To generate the report for all inline tests, replace `r1` with `r0` in the generated tests dir, inline tests dir and execution report (`${HOME}/exli/r1-its` -> `${HOME}/exli/r0-its`, `${HOME}/exli/results/r1-its-report` -> `${HOME}/exli/results/r0-its-report` and `${HOME}/exli/results/r1-its-report` to `${HOME}/exli/results/r0-its-report`)
> 
> The difference between "r0-its-report" and "r1-its-report" is that the "r0-its-report" contains all the inline tests, while the "r1-its-report" contains the inline tests that are reduced by the Round 1 Reducer (based on coverage)

> Alternatively, to use the default setting for output dirs `python -m exli.main batch_run_inline_tests --test_project_name=Bernardo-MG_velocity-config-tool`, this will run the inline tests for both reduced and all inline tests 

After running the inline tests, we can analyze the inline tests reports to get all passed and failed inline tests.

```bash
python -m exli.main analyze_inline_tests_reports --inline_test_type=r0
```

```bash
python -m exli.main analyze_inline_tests_reports --inline_test_type=r1
```

The report shows the number of tests, errors, failures, and time. For example,
```json
{
    "testsuite": {
        "@errors": "0",
        "@failures": "0",
        "@hostname": "bafe0a4bce5a",
        "@name": "JUnit Jupiter",
        "@skipped": "0",
        "@tests": "6",
        "@time": "0.042",
        ...
    }
}
```


> It is possible to see the message "Some inline tests failed for {project_name} {sha} during execution" because not all generated inline tests can be compiled or executed successfully. For example, if the user-defined class does not override the `toString()` method, the serialized object will contain the class name and the hash code, and the new object will not be equal to the original object when we run the inline tests and compare the objects (the collected value does not equal to the runtime value).
> 
> If there are inline tests failed because of compilation, we directly remove these failed inline tests, the log file `${HOME}/exli/results/r1-its-report/Bernardo-MG_velocity-config-tool-comp-failed-tests.txt` stores the failed inline tests and the reason why they failed (This project does not have compilation failed inline tests so this file does not exist).
>
> If inline tests failed because of execution, run the following command to remove the failed inline tests:
> 
> `python -m exli.main remove_failed_tests --inline_test_type=r1` (or `r0`)
>
> Re-generate test reports:
> 
> `python -m exli.main batch_run_inline_tests --test_project_name=Bernardo-MG_velocity-config-tool`


The generated execution result can be found at

`${HOME}/exli/results/r1-its-report/Bernardo-MG_velocity-config-tool-26226f5.json`

`${HOME}/exli/results/r0-its-report/Bernardo-MG_velocity-config-tool-26226f5.json`

#### Step 4: Generate mutants and run mutation analysis

In `exli/python` directory

Generate mutants:
```bash
python -m exli.main generate_mutants --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --target_stmts_path=${HOME}/exli/results/target-stmt/Bernardo-MG_velocity-config-tool-26226f5.txt --output_path=${HOME}/exli/results/mutants/Bernardo-MG_velocity-config-tool-26226f5-universalmutator.json
```
> Alternatively, to use the default settings `python -m exli.main batch_generate_mutants --test_project_name=Bernardo-MG_velocity-config-tool`

The generated mutants are in `${HOME}/exli/results/mutants/Bernardo-MG_velocity-config-tool-26226f5-universalmutator.json`

Run mutation analysis:
```bash
python -m exli.eval run_tests_with_mutants --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --test_types="['r0', 'r1']" --mutator=universalmutator --log_path=${HOME}/exli/log/run-tests-with-mutants.log
```
> Alternatively, to use the default settings `python -m exli.eval batch_run_tests_with_mutants --test_project_name=Bernardo-MG_velocity-config-tool`

The generated mutation analysis report are in
`${HOME}/exli/results/mutants-eval-results/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-r0.json`
and
`${HOME}/exli/results/mutants-eval-results/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-r1.json`


#### Step 5: Test reduction
```bash
python -m exli.eval get_r2_tests --project_name=Bernardo-MG_velocity-config-tool --sha=26226f5 --mutator=universalmutator --algo=greedy --output_path=${HOME}/exli/results/r2/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-greedy.txt
```

`${HOME}/exli/results/minimized` stores the minimized tests by 4
different algorithms: `Greedy`, `GE`, `GRE`,
`HGS`, which are called r2 tests in the paper.  For
example, the minimized tests by greedy algorithm for the project
`Bernardo-MG_velocity-config-tool` at commit `26226f5` are stored in
`${HOME}/exli/results/minimized/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-greedy.txt`

```txt
Bernardo-MG_velocity-config-tool#com.bernardomg.velocity.tool.ConfigTool_200Test#testLine204()#r1
Bernardo-MG_velocity-config-tool#com.bernardomg.velocity.tool.ConfigTool_288Test#testLine290()#r1
Bernardo-MG_velocity-config-tool#com.bernardomg.velocity.tool.ConfigTool_288Test#testLine302()#r0
```

Tests that end with `#r0` are from R0 tests, end with `#r1` are from R1 tests. These 3 tests are the minimized tests (`r2` tests) by the greedy algorithm.

`${HOME}/exli/results/itests-without-mutants` stores the inline tests whose target statements do not have mutants. For example, the inline tests for the project `Bernardo-MG_velocity-config-tool` at commit `26226f5` are stored in `${HOME}/exli/results/itests-without-mutants/Bernardo-MG_velocity-config-tool-26226f5-universalmutator.txt`

```txt
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;197
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;198
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;199
```

After merging `${HOME}/exli/results/minimized/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-greedy.txt` and `${HOME}/exli/results/itests-without-mutants/Bernardo-MG_velocity-config-tool-26226f5-universalmutator.txt`, the final r2 tests are stored in `${HOME}/exli/results/r2/Bernardo-MG_velocity-config-tool-26226f5-universalmutator-greedy.txt`

```txt
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;200;204;r1
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;288;290;r1
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;288;302;r0
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;197;r1
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;198;r1
Bernardo-MG_velocity-config-tool;com.bernardomg.velocity.tool.ConfigTool;195;199;r1
```

> Running `python -m exli.eval batch_get_r2_tests` will merge all the minized tests with greedy algorithm into one file `${HOME}/exli/results/r2-universalmutator-greedy-passed-tests.txt`

### Reproduce the results in the paper
See the [Reproduce the results](./REPRODUCE.md) for more details.

## Citation
If you have used ExLi in a research project, please cite the research paper in any related publication:

Title: [Extracting Inline Tests from Unit Tests](https://dl.acm.org/doi/abs/10.1145/3597926.3598149)

Authors: [Yu Liu](https://sweetstreet.github.io/), [Pengyu Nie](https://pengyunie.github.io/), [Anna Guo](https://www.linkedin.com/in/anna-y-guo/), [Milos Gligoric](http://users.ece.utexas.edu/~gligoric/), [Owolabi Legunsen](https://mir.cs.illinois.edu/legunsen/)

```bibtex
@inproceedings{LiuISSTA23EXLI,
  title =        {Extracting Inline Tests from Unit Tests},
  author =       {Yu Liu and Pengyu Nie and Anna Guo and Milos Gligoric and Owolabi Legunsen},
  pages =        {1--13},
  booktitle =    {Proceedings of the 32nd ACM SIGSOFT International Symposium on Software Testing and Analysis},
  year =         {2023},
}
```

```bibtex
@inproceedings{LiuFSE24EXLI,
  title =        {ExLi: An Inline-Test Generation Tool for Java},
  author =       {Yu Liu and Aditya Thimmaiah and Owolabi Legunsen and Milos Gligoric},
  pages =        {1--5},
  booktitle =    {Proceedings of the 32nd ACM Joint European Software Engineering Conference and Symposium on the Foundations of Software Engineering (Demonstrations)},
  year =         {2024},
}
```

[paper-url]: https://dl.acm.org/doi/10.1145/3597926.3598149
[itest-url]: https://github.com/EngineeringSoftware/inlinetest
