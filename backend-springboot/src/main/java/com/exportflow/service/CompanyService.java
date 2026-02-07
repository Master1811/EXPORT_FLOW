package com.exportflow.service;

import com.exportflow.dto.company.CompanyCreateRequest;
import com.exportflow.dto.company.CompanyResponse;
import com.exportflow.entity.Company;
import com.exportflow.entity.User;
import com.exportflow.exception.ResourceNotFoundException;
import com.exportflow.repository.CompanyRepository;
import com.exportflow.repository.UserRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class CompanyService {

    private final CompanyRepository companyRepository;
    private final UserRepository userRepository;

    @Transactional
    public CompanyResponse create(CompanyCreateRequest data, CurrentUser user) {
        String companyId = IdUtils.generateId();
        Company company = new Company();
        company.setId(companyId);
        company.setName(data.getName());
        company.setGstin(data.getGstin());
        company.setPan(data.getPan());
        company.setIecCode(data.getIecCode());
        company.setAddress(data.getAddress());
        company.setCity(data.getCity());
        company.setState(data.getState());
        company.setCountry(data.getCountry() != null ? data.getCountry() : "India");
        company.setBankAccount(data.getBankAccount());
        company.setBankIfsc(data.getBankIfsc());
        company.setOwnerId(user.getId());
        company.setCreatedAt(DateTimeUtils.nowIso());
        companyRepository.save(company);

        User u = userRepository.findById(user.getId()).orElseThrow();
        u.setCompanyId(companyId);
        userRepository.save(u);

        return toResponse(company);
    }

    public CompanyResponse get(String companyId) {
        Company company = companyRepository.findById(companyId)
            .orElseThrow(() -> new ResourceNotFoundException("Company not found"));
        return toResponse(company);
    }

    @Transactional
    public CompanyResponse update(String companyId, CompanyCreateRequest data) {
        Company company = companyRepository.findById(companyId)
            .orElseThrow(() -> new ResourceNotFoundException("Company not found"));
        if (data.getName() != null) company.setName(data.getName());
        if (data.getGstin() != null) company.setGstin(data.getGstin());
        if (data.getPan() != null) company.setPan(data.getPan());
        if (data.getIecCode() != null) company.setIecCode(data.getIecCode());
        if (data.getAddress() != null) company.setAddress(data.getAddress());
        if (data.getCity() != null) company.setCity(data.getCity());
        if (data.getState() != null) company.setState(data.getState());
        if (data.getCountry() != null) company.setCountry(data.getCountry());
        if (data.getBankAccount() != null) company.setBankAccount(data.getBankAccount());
        if (data.getBankIfsc() != null) company.setBankIfsc(data.getBankIfsc());
        company.setUpdatedAt(DateTimeUtils.nowIso());
        companyRepository.save(company);
        return toResponse(company);
    }

    private CompanyResponse toResponse(Company c) {
        return CompanyResponse.builder()
            .id(c.getId())
            .name(c.getName())
            .gstin(c.getGstin())
            .pan(c.getPan())
            .iecCode(c.getIecCode())
            .address(c.getAddress())
            .city(c.getCity())
            .state(c.getState())
            .country(c.getCountry() != null ? c.getCountry() : "India")
            .createdAt(c.getCreatedAt())
            .build();
    }
}
