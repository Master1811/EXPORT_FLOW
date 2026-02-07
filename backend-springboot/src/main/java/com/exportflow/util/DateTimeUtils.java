package com.exportflow.util;

import java.time.Instant;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

public final class DateTimeUtils {

    private static final DateTimeFormatter ISO_FORMAT = DateTimeFormatter.ISO_INSTANT;

    private DateTimeUtils() {}

    public static String nowIso() {
        return ISO_FORMAT.format(Instant.now().atZone(ZoneOffset.UTC));
    }
}
