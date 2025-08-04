PLATFORM_RULES = {
    "facebook": {
        "text_limit": 63206,
        "hashtag_limit": "Unlimited (2-5 recommended)",
        "note": "Avoid overusing hashtags/spammy text.",
        "links": "Allowed with previews",
    },
    "instagram_feed": {
        "text_limit": 2200,
        "hashtag_limit": "30 max",
        "mentions": "20 users max",
        "links": "Not clickable in captions",
    },
    "instagram_threads": {
        "text_limit": 500,
        "hashtag_limit": "Only 1 allowed",
        "notes": "Hashtags mostly decorative",
    },
    "x": {
        "text_limit": 280,
        "hashtag_limit": "No limit (1-2 recommended)",
        "notes": "Links take 23 chars. Emojis count as 2 chars.",
    },
    "linkedin": {
        "text_limit": 3000,
        "hashtag_limit": "5 recommended",
        "notes": "Avoid spammy tags like #like4like",
    }
}



PLATFORM_RULES_WITH_INSIGHT = {
    "facebook": {
        "text_limit": 63206,
        "hashtag_limit": "Unlimited (2-5 recommended)",
        "notes": "Avoid spammy tags. Use casual, relatable tone. Links allowed.",
        "slang": "Keep it personal, spark conversations, tag friends.",
    },
    "instagram_feed": {
        "text_limit": 2200,
        "hashtag_limit": "30 max",
        "mentions": "20 users max",
        "notes": "Use aesthetic captions. Add relevant hashtags and emojis.",
        "slang": "Vibes, aesthetic, drop a ❤️, outfit check",
    },
    "instagram_threads": {
        "text_limit": 500,
        "hashtag_limit": "Only 1 allowed",
        "notes": "Threads are conversational. Hashtags are decorative.",
        "slang": "Real talk, hot take, let's unpack this",
    },
    "x": {
        "text_limit": 280,
        "hashtag_limit": "No limit (1-2 recommended)",
        "notes": "Concise. Sharp tone. Link = 23 chars, emojis = 2 chars.",
        "slang": "Hot take, thread 🧵, don't @ me",
    },
    "linkedin": {
        "text_limit": 3000,
        "hashtag_limit": "5 recommended",
        "notes": "Professional tone. Avoid spammy tags like #like4like.",
        "slang": "Excited to share, humbled to announce, let's connect, lengthy post",
    }
}

