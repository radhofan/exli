/*
 * Copyright (C) 2007-2020 Crafter Software Corporation. All Rights Reserved.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 3 as published by
 * the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package org.craftercms.core.url.impl;

import org.apache.commons.lang3.ArrayUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.craftercms.core.service.CachingOptions;
import org.craftercms.core.service.Context;
import org.craftercms.core.url.UrlTransformer;
import org.craftercms.core.util.UrlUtils;
import org.inlinetest.Here;
import static org.inlinetest.Here.group;

/**
 * Class description goes HERE
 *
 * @author Sumer Jabri
 * @author Alfonso Vásquez
 */
public class LongToShortUrlTransformer implements UrlTransformer {

    private static final Log logger = LogFactory.getLog(LongToShortUrlTransformer.class);

    public static final String URL_NUMBERED_NAME_REGEX = "\\b\\d*_(.+)\\b";

    public static final int URL_NUMBERED_NAME_REGEX_SHORT_NAME_GROUP = 1;

    private String containsShortNameRegex;

    private int shortNameRegexGroup;

    public LongToShortUrlTransformer() {
        containsShortNameRegex = URL_NUMBERED_NAME_REGEX;
        shortNameRegexGroup = URL_NUMBERED_NAME_REGEX_SHORT_NAME_GROUP;
    }

    public void setContainsShortNameRegex(String containsShortNameRegex) {
        this.containsShortNameRegex = containsShortNameRegex;
    }

    public void setShortNameRegexGroup(int shortNameRegexGroup) {
        this.shortNameRegexGroup = shortNameRegexGroup;
    }

    protected String getShortUrl(String longUrl) {
        String[] levels = StringUtils.strip(longUrl, "/").split("/");
        new Here("Randoop", 57).given(longUrl, "TaggingByPathProcessor{newField='null', pathMapping=null}").checkEq(levels, new String[] { "TaggingByPathProcessor{newField='null', pathMapping=null}" });
        new Here("Randoop", 57).given(longUrl, "ExcludeByUrlItemFilter{excludeRegexes=[, hi!, hi!, item-list, /clear, item-list]}").checkEq(levels, new String[] { "ExcludeByUrlItemFilter{excludeRegexes=[, hi!, hi!, item-list, ", "clear, item-list]}" });
        new Here("Randoop", 57).given(longUrl, "contentStoreService.item").checkEq(levels, new String[] { "contentStoreService.item" });
        new Here("Unit", 57).given(longUrl, "/001_folder/002_subfolder/003_index.html/").checkEq(levels, new String[] { "001_folder", "002_subfolder", "003_index.html" });
        new Here("Randoop", 57).given(longUrl, "[]").checkEq(levels, new String[] { "[]" });
        StringBuilder result = new StringBuilder();
        if (ArrayUtils.isNotEmpty(levels)) {
            for (String level : levels) {
                result.append("/").append(UrlUtils.getShortName(level, containsShortNameRegex, shortNameRegexGroup));
            }
        }
        if (longUrl.endsWith("/")) {
            result.append("/");
        }
        return result.toString();
    }

    public String transformUrl(Context context, CachingOptions cachingOptions, String url) {
        String result = getShortUrl(url);
        if (logger.isDebugEnabled()) {
            logger.debug("Transformation in: " + url + ", Transformation out: " + result);
        }
        return result;
    }
}
