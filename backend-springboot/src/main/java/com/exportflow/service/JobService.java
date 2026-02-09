package com.exportflow.service;

import com.exportflow.dto.jobs.JobStatusResponse;
import com.exportflow.entity.Job;
import com.exportflow.exception.ResourceNotFoundException;
import com.exportflow.repository.JobRepository;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class JobService {

    private final JobRepository jobRepository;

    public JobStatusResponse getStatus(String jobId) {
        Job job = jobRepository.findById(jobId)
            .orElseThrow(() -> new ResourceNotFoundException("Job not found"));
        return JobStatusResponse.builder()
            .jobId(jobId)
            .status(job.getStatus() != null ? job.getStatus() : "unknown")
            .progress(job.getProgress() != null ? job.getProgress() : 0)
            .result(job.getResult())
            .createdAt(job.getCreatedAt() != null ? job.getCreatedAt() : DateTimeUtils.nowIso())
            .build();
    }
}
