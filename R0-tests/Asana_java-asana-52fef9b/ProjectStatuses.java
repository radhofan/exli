package com.asana.resources;

import com.asana.Client;
import com.asana.models.ProjectStatus;
import com.asana.requests.CollectionRequest;
import com.asana.requests.ItemRequest;
import com.asana.resources.gen.ProjectStatusesBase;
import org.inlinetest.Here;
import static org.inlinetest.Here.group;

public class ProjectStatuses extends ProjectStatusesBase {

    public ProjectStatuses(Client client) {
        super(client);
    }

    /**
     * Creates a new status update on the project.
     *
     * Returns the full record of the newly created project status update.
     *
     * @param  project The project on which to create a status update.
     * @return Request object
     */
    public ItemRequest<ProjectStatus> createInProject(String project) {
        String path = String.format("/projects/%s/project_statuses", project);
        new Here("Randoop", 24).given(project, "/tasks/Not Found/removeProject").checkEq(path, "/projects//tasks/Not Found/removeProject/project_statuses");
        new Here("Randoop", 24).given(project, "hi!").checkEq(path, "/projects/hi!/project_statuses");
        new Here("Randoop", 24).given(project, "Server Error").checkEq(path, "/projects/Server Error/project_statuses");
        new Here("Randoop", 24).given(project, "Not Found").checkEq(path, "/projects/Not Found/project_statuses");
        new Here("Randoop", 24).given(project, "200").checkEq(path, "/projects/200/project_statuses");
        new Here("Randoop", 24).given(project, "").checkEq(path, "/projects//project_statuses");
        return new ItemRequest<ProjectStatus>(this, ProjectStatus.class, path, "POST");
    }

    /**
     * Returns the compact project status update records for all updates on the project.
     *
     * @param  project The project to find status updates for.
     * @return Request object
     */
    public CollectionRequest<ProjectStatus> findByProject(String project) {
        String path = String.format("/projects/%s/project_statuses", project);
        new Here("Randoop", 36).given(project, "").checkEq(path, "/projects//project_statuses");
        new Here("Randoop", 36).given(project, "POST").checkEq(path, "/projects/POST/project_statuses");
        new Here("Randoop", 36).given(project, "Not Found").checkEq(path, "/projects/Not Found/project_statuses");
        return new CollectionRequest<ProjectStatus>(this, ProjectStatus.class, path, "GET");
    }

    /**
     * Returns the complete record for a single status update.
     *
     * @param  projectStatus The project status update to get.
     * @return Request object
     */
    public ItemRequest<ProjectStatus> findById(String projectStatus) {
        String path = String.format("/project_statuses/%s", projectStatus);
        new Here("Randoop", 48).given(projectStatus, "Invalid Request").checkEq(path, "/project_statuses/Invalid Request");
        new Here("Randoop", 48).given(projectStatus, "https://app.asana.com/-/oauth_authorize?client_id&redirect_uri=hi!&response_type=code&state=Invalid%20Request").checkEq(path, "/project_statuses/https://app.asana.com/-/oauth_authorize?client_id&redirect_uri=hi!&response_type=code&state=Invalid%20Request");
        new Here("Randoop", 48).given(projectStatus, "Server Error").checkEq(path, "/project_statuses/Server Error");
        new Here("Randoop", 48).given(projectStatus, "POST").checkEq(path, "/project_statuses/POST");
        return new ItemRequest<ProjectStatus>(this, ProjectStatus.class, path, "GET");
    }

    /**
     * Deletes a specific, existing project status update.
     *
     * Returns an empty data record.
     *
     * @param  projectStatus The project status update to delete.
     * @return Request object
     */
    public ItemRequest<ProjectStatus> delete(String projectStatus) {
        String path = String.format("/project_statuses/%s", projectStatus);
        new Here("Randoop", 62).given(projectStatus, "POST").checkEq(path, "/project_statuses/POST");
        new Here("Randoop", 62).given(projectStatus, "hi!").checkEq(path, "/project_statuses/hi!");
        return new ItemRequest<ProjectStatus>(this, ProjectStatus.class, path, "DELETE");
    }
}
