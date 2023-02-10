/*
 * Copyright (c) 2010-2022 Mark Allen, Norbert Bartels.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package com.restfb.util;

import static java.lang.String.format;
import static java.net.URLDecoder.decode;
import static java.net.URLEncoder.encode;
import static java.util.Collections.emptyMap;
import static java.util.stream.Collectors.toList;
import java.io.UnsupportedEncodingException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;
import org.inlinetest.Here;
import static org.inlinetest.Here.group;

/**
 * @author <a href="http://restfb.com">Mark Allen</a>
 * @since 1.6.10
 */
public final class UrlUtils {

    /**
     * Prevents instantiation.
     */
    private UrlUtils() {
        throw new IllegalStateException("UrlUtils must not be instantiated");
    }

    /**
     * URL-encodes a string.
     * <p>
     * Assumes {@code string} is in {@link StandardCharsets#UTF_8} format.
     *
     * @param string
     *          The string to URL-encode.
     * @return The URL-encoded version of the input string, or {@code null} if {@code string} is {@code null}.
     * @throws IllegalStateException
     *           If unable to URL-encode because the JVM doesn't support {@link StandardCharsets#UTF_8}.
     */
    public static String urlEncode(String string) {
        if (string == null) {
            return null;
        }
        try {
            return encode(string, StandardCharsets.UTF_8.name());
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("Platform doesn't support " + StandardCharsets.UTF_8.name(), e);
        }
    }

    /**
     * URL-decodes a string.
     * <p>
     * Assumes {@code string} is in {@link StandardCharsets#UTF_8} format.
     *
     * @param string
     *          The string to URL-decode.
     * @return The URL-decoded version of the input string, or {@code null} if {@code string} is {@code null}.
     * @throws IllegalStateException
     *           If unable to URL-decode because the JVM doesn't support {@link StandardCharsets#UTF_8}.
     * @since 1.6.5
     */
    public static String urlDecode(String string) {
        if (string == null) {
            return null;
        }
        try {
            return decode(string, StandardCharsets.UTF_8.name());
        } catch (UnsupportedEncodingException e) {
            throw new IllegalStateException("Platform doesn't support " + StandardCharsets.UTF_8.name(), e);
        }
    }

    /**
     * For the given {@code queryString}, extract a mapping of query string parameter names to values.
     * <p>
     * Example of a {@code queryString} is {@code accessToken=123&expires=345}.
     *
     * @param queryString
     *          The URL query string from which parameters are extracted.
     * @return A mapping of query string parameter names to values. If {@code queryString} is {@code null}, an empty
     *         {@code Map} is returned.
     * @throws IllegalStateException
     *           If unable to URL-decode because the JVM doesn't support {@link StandardCharsets#UTF_8}.
     */
    public static Map<String, List<String>> extractParametersFromQueryString(String queryString) {
        if (queryString == null) {
            return emptyMap();
        }
        // If there is no ? character at the front of the string, append it.
        return extractParametersFromUrl(format("restfb://url%s", queryString.startsWith("?") ? queryString : "?" + queryString));
    }

    /**
     * For the given {@code url}, extract a mapping of query string parameter names to values.
     * <p>
     * Adapted from an implementation by BalusC and dfrankow, available at
     * http://stackoverflow.com/questions/1667278/parsing-query-strings-in-java.
     *
     * @param url
     *          The URL from which parameters are extracted.
     * @return A mapping of query string parameter names to values. If {@code url} is {@code null}, an empty {@code Map}
     *         is returned.
     * @throws IllegalStateException
     *           If unable to URL-decode because the JVM doesn't support {@link StandardCharsets#UTF_8}.
     */
    public static Map<String, List<String>> extractParametersFromUrl(String url) {
        if (url == null) {
            return emptyMap();
        }
        Map<String, List<String>> parameters = new HashMap<>();
        String[] urlParts = url.split("\\?");
        new Here("Randoop", 138).given(url, "public_profile,pages_manage_cta").checkEq(urlParts, new String[] { "public_profile,pages_manage_cta" });
        new Here("Unit", 138).given(url, "restfb://url?https://graph.facebook.com/v3.1/device/login_status").checkEq(urlParts, new String[] { "restfb://url", "https://graph.facebook.com/v3.1/device/login_status" });
        new Here("Unit", 138).given(url, "http://whatever?access_token=123").checkEq(urlParts, new String[] { "http://whatever", "access_token=123" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=123&first=6543&before=1234").checkEq(urlParts, new String[] { "restfb://url", "access_token=123&first=6543&before=1234" });
        new Here("Unit", 138).given(url, "").checkEq(urlParts, new String[] { "" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=accesstoken&token_type=tokentype&expires=132363").checkEq(urlParts, new String[] { "restfb://url", "access_token=accesstoken&token_type=tokentype&expires=132363" });
        new Here("Unit", 138).given(url, "access_token=123").checkEq(urlParts, new String[] { "access_token=123" });
        new Here("Unit", 138).given(url, "?access_token=123").checkEq(urlParts, new String[] { "", "access_token=123" });
        new Here("Randoop", 138).given(url, "restfb://url?{}").checkEq(urlParts, new String[] { "restfb://url", "{}" });
        new Here("Randoop", 138).given(url, "restfb://url?").checkEq(urlParts, new String[] { "restfb://url" });
        new Here("Randoop", 138).given(url, "audio").checkEq(urlParts, new String[] { "audio" });
        new Here("Randoop", 138).given(url, "restfb://url?WebhookObject(object=null, entryList=[])").checkEq(urlParts, new String[] { "restfb://url", "WebhookObject(object=null, entryList=[])" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=123").checkEq(urlParts, new String[] { "restfb://url", "access_token=123" });
        new Here("Unit", 138).given(url, "restfb://url?").checkEq(urlParts, new String[] { "restfb://url" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=<access-token>&expires_in=5184000").checkEq(urlParts, new String[] { "restfb://url", "access_token=<access-token>&expires_in=5184000" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=<access-token>&expires=5184000").checkEq(urlParts, new String[] { "restfb://url", "access_token=<access-token>&expires=5184000" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=123&before=1234").checkEq(urlParts, new String[] { "restfb://url", "access_token=123&before=1234" });
        new Here("Randoop", 138).given(url, "restfb://url?true=AirlineFieldItem(label=null, value=null)").checkEq(urlParts, new String[] { "restfb://url", "true=AirlineFieldItem(label=null, value=null)" });
        new Here("Unit", 138).given(url, "restfb://url?access_token=accesstoken&expires=132363").checkEq(urlParts, new String[] { "restfb://url", "access_token=accesstoken&expires=132363" });
        if (urlParts.length > 1) {
            String query = urlParts[1];
            parameters = // 
            Pattern.compile("&").splitAsStream(query).map(s -> Arrays.copyOf(s.split("="), 2)).collect(Collectors.groupingBy(s -> urlDecode(s[0]), Collectors.mapping(s -> urlDecode(s[1]), toList())));
            new Here("Randoop", 142).given(query, "{}").checkEq(parameters, "115.xml");
            new Here("Unit", 142).given(query, "access_token=accesstoken&token_type=tokentype&expires=132363").checkEq(parameters, "103.xml");
            new Here("Unit", 142).given(query, "https://graph.facebook.com/v3.1/device/login_status").checkEq(parameters, "101.xml");
            new Here("Unit", 142).given(query, "access_token=123&before=1234").checkEq(parameters, "4.xml");
            new Here("Unit", 142).given(query, "access_token=accesstoken&expires=132363").checkEq(parameters, "104.xml");
            new Here("Unit", 142).given(query, "access_token=123").checkEq(parameters, "3.xml");
            new Here("Randoop", 142).given(query, "true=AirlineFieldItem(label=null, value=null)").checkEq(parameters, "119.xml");
            new Here("Randoop", 142).given(query, "WebhookObject(object=null, entryList=[])").checkEq(parameters, "120.xml");
            new Here("Unit", 142).given(query, "access_token=<access-token>&expires=5184000").checkEq(parameters, "99.xml");
            new Here("Unit", 142).given(query, "access_token=<access-token>&expires_in=5184000").checkEq(parameters, "110.xml");
            new Here("Unit", 142).given(query, "access_token=123&first=6543&before=1234").checkEq(parameters, "5.xml");
        }
        return parameters;
    }

    /**
     * Modify the query string in the given {@code url} and return the new url as String.
     * <p>
     * The given key/value pair is added to the url. If the key is already present, it is replaced with the new value.
     *
     * @param url
     *          The URL which parameters should be modified.
     * @param key
     *          the key, that should be modified or added
     * @param value
     *          the value of the key/value pair
     * @return the modified URL as String
     */
    public static String replaceOrAddQueryParameter(String url, String key, String value) {
        String[] urlParts = url.split("\\?");
        new Here("Randoop", 164).given(url, "").checkEq(urlParts, new String[] { "" });
        new Here("Randoop", 164).given(url, "linked").checkEq(urlParts, new String[] { "linked" });
        new Here("Unit", 164).given(url, "http://www.example.com").checkEq(urlParts, new String[] { "http://www.example.com" });
        new Here("Randoop", 164).given(url, "hi!").checkEq(urlParts, new String[] { "hi!" });
        new Here("Randoop", 164).given(url, "linked?true=AirlineFieldItem(label=null, value=null)").checkEq(urlParts, new String[] { "linked", "true=AirlineFieldItem(label=null, value=null)" });
        new Here("Unit", 164).given(url, "http://www.example.com?access_token=123&before=1234").checkEq(urlParts, new String[] { "http://www.example.com", "access_token=123&before=1234" });
        new Here("Unit", 164).given(url, "http://www.example.com?access_token=123").checkEq(urlParts, new String[] { "http://www.example.com", "access_token=123" });
        new Here("Randoop", 164).given(url, "https://graph-video.facebook.com").checkEq(urlParts, new String[] { "https://graph-video.facebook.com" });
        String qParameter = key + "=" + value;
        if (urlParts.length == 2) {
            Map<String, List<String>> paramMap = extractParametersFromQueryString(urlParts[1]);
            if (paramMap.containsKey(key)) {
                String queryValue = paramMap.get(key).get(0);
                return url.replace(key + "=" + queryValue, qParameter);
            } else {
                return url + "&" + qParameter;
            }
        } else {
            return url + "?" + qParameter;
        }
    }

    /**
     * Remove the given key from the url query string and return the new URL as String.
     *
     * @param url
     *          The URL from which parameters are extracted.
     * @param key
     *          the key, that should be removed
     * @return the modified URL as String
     */
    public static String removeQueryParameter(String url, String key) {
        String[] urlParts = url.split("\\?");
        new Here("Randoop", 191).given(url, "Long[]").checkEq(urlParts, new String[] { "Long[]" });
        new Here("Randoop", 191).given(url, "[\n\t\"QuickReplyItem(payload=null)\",\n\t-1\n]").checkEq(urlParts, new String[] { "[\n\t\"QuickReplyItem(payload=null)\",\n\t-1\n]" });
        new Here("Unit", 191).given(url, "http://www.example.com?access_token=123&first=6543&before=1234").checkEq(urlParts, new String[] { "http://www.example.com", "access_token=123&first=6543&before=1234" });
        new Here("Unit", 191).given(url, "http://www.example.com?access_token=123&before=1234").checkEq(urlParts, new String[] { "http://www.example.com", "access_token=123&before=1234" });
        new Here("Randoop", 191).given(url, "Change(field=hi!, value=null, userObjectVerb=null, rawValue=null)").checkEq(urlParts, new String[] { "Change(field=hi!, value=null, userObjectVerb=null, rawValue=null)" });
        new Here("Randoop", 191).given(url, "WebhookEntry(uid=, id=null, time=Fri Jan 13 01:03:26 CST 2023, rawTime=null, changedFields=[], changes=[], messaging=[], standby=[])").checkEq(urlParts, new String[] { "WebhookEntry(uid=, id=null, time=Fri Jan 13 01:03:26 CST 2023, rawTime=null, changedFields=[], changes=[], messaging=[], standby=[])" });
        if (urlParts.length == 2) {
            Map<String, List<String>> paramMap = extractParametersFromQueryString(urlParts[1]);
            if (paramMap.containsKey(key)) {
                String queryValue = paramMap.get(key).get(0);
                String result = url.replace(key + "=" + queryValue, "");
                new Here("Unit", 197).given(queryValue, "1234").given(key, "before").given(url, "http://www.example.com?access_token=123&before=1234").checkEq(result, "http://www.example.com?access_token=123&");
                new Here("Unit", 197).given(queryValue, "6543").given(key, "first").given(url, "http://www.example.com?access_token=123&first=6543&before=1234").checkEq(result, "http://www.example.com?access_token=123&&before=1234");
                new Here("Unit", 197).given(queryValue, "123").given(key, "access_token").given(url, "http://www.example.com?access_token=123&before=1234").checkEq(result, "http://www.example.com?&before=1234");
                // improper separators have to be fixed
                // @TODO find a better way to solve this
                result = result.replace("?&", "?").replace("&&", "&");
                new Here("Unit", 200).given(result, "http://www.example.com?&before=1234").checkEq(result, "http://www.example.com?before=1234");
                new Here("Unit", 200).given(result, "http://www.example.com?access_token=123&&before=1234").checkEq(result, "http://www.example.com?access_token=123&before=1234");
                new Here("Unit", 200).given(result, "http://www.example.com?access_token=123&").checkEq(result, "http://www.example.com?access_token=123&");
                if (result.endsWith("&")) {
                    return result.substring(0, result.length() - 1);
                } else {
                    return result;
                }
            }
        }
        return url;
    }
}
