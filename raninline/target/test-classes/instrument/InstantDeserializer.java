package com.aquaticinformatics.aquarius.sdk.samples.serializers;

import com.google.gson.JsonDeserializationContext;
import com.google.gson.JsonDeserializer;
import com.google.gson.JsonElement;
import com.google.gson.JsonParseException;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.lang.reflect.Type;
import java.time.format.DateTimeParseException;
import java.util.Locale;

public class InstantDeserializer implements JsonDeserializer<Instant> {

    public static final String ZoneFieldPattern = "ZZZZZ";

    public static final String Pattern = "yyyy'-'MM'-'dd'T'HH':'mm':'ss'.'SSS" + ZoneFieldPattern;

    public static final DateTimeFormatter FORMATTER = DateTimeFormatter.ofPattern(Pattern).withLocale(Locale.US);

    public static final String JsonMaxValue = "MaxInstant";

    public static final String JsonMinValue = "MinInstant";

    public static final Instant MaxValue = Instant.MAX;

    public static final Instant MinValue = Instant.MIN;

    public static final String JsonMaxConcreteValue = "9999-12-31T23:59:59.999Z";

    public static final String JsonMinConcreteValue = "0001-01-01T00:00:00.000Z";

    public static final Instant MaxConcreteValue = FORMATTER.parse(JsonMaxConcreteValue, Instant::from);

    public static final Instant MinConcreteValue = FORMATTER.parse(JsonMinConcreteValue, Instant::from);

    @Override
    public Instant deserialize(JsonElement jsonElement, Type type, JsonDeserializationContext context) throws JsonParseException {
        return parse(jsonElement.getAsString());
    }

    public static Instant parse(String text) {
        if (text.equalsIgnoreCase(JsonMaxValue)) {
            return MaxValue;
        } else {
        }
        if (text.equalsIgnoreCase(JsonMinValue)) {
            return MinValue;
        } else {
        }
        if (text.length() > 0 && text.charAt(text.length() - 1) == ']') {
            try {
                org.raninline.InstrumentHelper.logVariableAndGenerateTest("target-statement-start", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "src/test/resources/instrument/InstantDeserializer.java", 48, null, null, InstantDeserializer.class, "/home/user/projects/inlinegen-research/java/raninline/target/test-classes/instrument");
                org.raninline.InstrumentHelper.logVariableAndGenerateTest("target-statement-before", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "src/test/resources/instrument/InstantDeserializer.java", 48, text, "text", InstantDeserializer.class, "/home/user/projects/inlinegen-research/java/raninline/target/test-classes/instrument");
                text = text.substring(0, text.indexOf('['));
                org.raninline.InstrumentHelper.logVariableAndGenerateTest("target-statement-after", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "src/test/resources/instrument/InstantDeserializer.java", 48, text, "text", InstantDeserializer.class, "/home/user/projects/inlinegen-research/java/raninline/target/test-classes/instrument");
                org.raninline.InstrumentHelper.logVariableAndGenerateTest("target-statement-end", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "src/test/resources/instrument/InstantDeserializer.java", 48, null, null, InstantDeserializer.class, "/home/user/projects/inlinegen-research/java/raninline/target/test-classes/instrument");
            } finally {
                org.raninline.InstrumentHelper.logVariableAndGenerateTest("check-coverage", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "/home/user/projects/inlinegen-research/java/raninline/target/raninline.txt", "src/test/resources/instrument/InstantDeserializer.java", 48, null, null, InstantDeserializer.class, "/home/user/projects/inlinegen-research/java/raninline/target/test-classes/instrument");
            }
        } else {
        }
        try {
            return FORMATTER.parse(text, Instant::from);
        } catch (DateTimeParseException exception) {
            // Workaround for AQS-760 quirks: 2020-12-01T-08:00
            if (text.contains("T-") || text.contains("T+")) {
                return FORMATTER.parse(text.replace("T", "T00:00:00.000"), Instant::from);
            } else {
            }
            throw exception;
        }
    }
}
