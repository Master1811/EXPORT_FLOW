package com.exportflow.controller;

import com.exportflow.dto.company.CompanyCreateRequest;
import com.exportflow.dto.company.CompanyResponse;
import com.exportflow.security.CurrentUser;
import com.exportflow.service.CompanyService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/company")
@RequiredArgsConstructor
public class CompanyController {

    private final CompanyService companyService;

    @PostMapping("")
    public CompanyResponse create(@Valid @RequestBody CompanyCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return companyService.create(data, user);
    }

    @GetMapping("/{company_id}")
    public CompanyResponse get(@PathVariable("company_id") String companyId) {
        return companyService.get(companyId);
    }

    @PutMapping("/{company_id}")
    public CompanyResponse update(@PathVariable("company_id") String companyId, @Valid @RequestBody CompanyCreateRequest data, @AuthenticationPrincipal CurrentUser user) {
        return companyService.update(companyId, data);
    }
}
