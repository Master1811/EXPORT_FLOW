package com.exportflow.controller;

import com.exportflow.dto.jobs.JobStatusResponse;
import com.exportflow.service.JobService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import com.exportflow.security.CurrentUser;

@RestController
@RequestMapping("/jobs")
@RequiredArgsConstructor
public class JobController {

    private final JobService jobService;

    @GetMapping("/{job_id}/status")
    public JobStatusResponse getJobStatus(@PathVariable("job_id") String jobId, @AuthenticationPrincipal CurrentUser user) {
        return jobService.getStatus(jobId);
    }
}
