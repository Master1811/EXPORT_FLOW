package com.exportflow.service;

import com.exportflow.dto.forex.ForexRateCreateRequest;
import com.exportflow.dto.forex.ForexRateResponse;
import com.exportflow.entity.ForexRate;
import com.exportflow.repository.ForexRateRepository;
import com.exportflow.security.CurrentUser;
import com.exportflow.util.IdUtils;
import com.exportflow.util.DateTimeUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ForexService {

    private static final Map<String, Double> DEFAULT_RATES = Map.of(
        "USD", 83.50, "EUR", 91.20, "GBP", 106.50,
        "AED", 22.75, "JPY", 0.56, "CNY", 11.50, "SGD", 62.30
    );

    private final ForexRateRepository forexRateRepository;

    @Transactional
    public ForexRateResponse createRate(ForexRateCreateRequest data, CurrentUser user) {
        String rateId = IdUtils.generateId();
        ForexRate r = new ForexRate();
        r.setId(rateId);
        r.setCurrency(data.getCurrency());
        r.setRate(data.getRate());
        r.setSource(data.getSource() != null ? data.getSource() : "manual");
        r.setCompanyId(user.getCompanyId() != null ? user.getCompanyId() : user.getId());
        r.setTimestamp(DateTimeUtils.nowIso());
        forexRateRepository.save(r);
        return ForexRateResponse.builder()
            .id(r.getId())
            .currency(r.getCurrency())
            .rate(r.getRate())
            .source(r.getSource())
            .timestamp(r.getTimestamp())
            .build();
    }

    public Map<String, Object> getLatest() {
        String[] currencies = {"USD", "EUR", "GBP", "AED", "JPY", "CNY", "SGD"};
        Map<String, Double> rates = new HashMap<>();
        for (String curr : currencies) {
            forexRateRepository.findFirstByCurrencyOrderByTimestampDesc(curr)
                .ifPresentOrElse(r -> rates.put(curr, r.getRate()),
                    () -> rates.put(curr, DEFAULT_RATES.getOrDefault(curr, 1.0)));
        }
        return Map.of(
            "rates", rates,
            "base", "INR",
            "timestamp", DateTimeUtils.nowIso()
        );
    }

    public Map<String, Object> getHistory(String currency, int days) {
        List<ForexRate> rates = forexRateRepository.findByCurrencyOrderByTimestampDesc(
            currency, PageRequest.of(0, days));
        List<Map<String, Object>> history = rates.stream()
            .map(r -> Map.<String, Object>of(
                "id", r.getId(),
                "currency", r.getCurrency(),
                "rate", r.getRate(),
                "source", r.getSource(),
                "timestamp", r.getTimestamp()
            ))
            .toList();
        return Map.of("currency", currency, "history", history);
    }
}
