package com.exportflow.controller;

import com.exportflow.entity.FileEntity;
import com.exportflow.exception.ResourceNotFoundException;
import com.exportflow.repository.FileRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/files")
@RequiredArgsConstructor
public class FileController {

    private final FileRepository fileRepository;

    @PostMapping("/upload")
    public Map<String, Object> uploadFile(@RequestParam("file") MultipartFile file, @AuthenticationPrincipal CurrentUser user) {
        String fileId = IdUtils.generateId();
        String companyId = user.getCompanyId() != null ? user.getCompanyId() : user.getId();
        try {
            byte[] content = file.getBytes();
            FileEntity f = new FileEntity();
            f.setId(fileId);
            f.setFilename(file.getOriginalFilename());
            f.setContentType(file.getContentType());
            f.setSize(content.length);
            f.setCompanyId(companyId);
            f.setUploadedBy(user.getId());
            f.setCreatedAt(DateTimeUtils.nowIso());
            fileRepository.save(f);
            return Map.of(
                "id", fileId,
                "filename", file.getOriginalFilename() != null ? file.getOriginalFilename() : "file",
                "size", content.length
            );
        } catch (Exception e) {
            FileEntity f = new FileEntity();
            f.setId(fileId);
            f.setFilename(file.getOriginalFilename());
            f.setContentType(file.getContentType());
            f.setSize(0);
            f.setCompanyId(companyId);
            f.setUploadedBy(user.getId());
            f.setCreatedAt(DateTimeUtils.nowIso());
            fileRepository.save(f);
            return Map.of(
                "id", fileId,
                "filename", file.getOriginalFilename() != null ? file.getOriginalFilename() : "file",
                "size", 0
            );
        }
    }

    @GetMapping("/{file_id}")
    public Map<String, Object> getFile(@PathVariable("file_id") String fileId) {
        FileEntity f = fileRepository.findById(fileId)
            .orElseThrow(() -> new ResourceNotFoundException("File not found"));
        return Map.of(
            "id", f.getId(),
            "filename", f.getFilename() != null ? f.getFilename() : "",
            "content_type", f.getContentType() != null ? f.getContentType() : "",
            "size", f.getSize() != null ? f.getSize() : 0,
            "company_id", f.getCompanyId() != null ? f.getCompanyId() : "",
            "uploaded_by", f.getUploadedBy() != null ? f.getUploadedBy() : "",
            "created_at", f.getCreatedAt() != null ? f.getCreatedAt() : ""
        );
    }

    @DeleteMapping("/{file_id}")
    public Map<String, String> deleteFile(@PathVariable("file_id") String fileId) {
        if (!fileRepository.existsById(fileId)) {
            throw new ResourceNotFoundException("File not found");
        }
        fileRepository.deleteById(fileId);
        return Map.of("message", "File deleted");
    }
}
