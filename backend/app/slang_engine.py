import re

# Dictionaries of root slangs. We will store them in their standard spellings.
# Our matching engine will collapse both the input text and these dictionary words
# to ensure that variations like "kutta" -> "kuta" and "kuuuttttaaaa" -> "kuta" match perfectly.

LEVEL_3_EXTREME = {
    # Mother / Sister / Prostitute / Severe Family Insults
    "madarchod", "madarchodd", "madarchood", "madarchoot", "madarchut", "mc", "m.c.",
    "behenchod", "bhenchod", "bahenchod", "bhenchodd", "bc", "b.c.",
    "bhosdike", "bhosda", "bhosdaa", "bhonsdike", "bsdk", "b.s.d.k", "bhosdiki", 
    "bhosdiwala", "bhosdiwale", "bhosri", "bhosdi", "bhonsri", "bhosriwala",
    "bhenkelode", "bkl", "b.k.l.",
    "randi", "randy", "raand", "rand", "randwa", "randhwa", "chinaal", "chinal", "ghasti", "ghasti", "chhnnal",
    "bhadwa", "bhadwe", "bhadua", "bhadwaa", "bhandwa", "bhadwi", "bhadwon", "bhadwapanti",
    "pkmkb", "porkistan", "bhosadchodal", "bhosadchod"
}

LEVEL_2_INSULTS = {
    # Direct Insults / Genitals / Sexist / Sexual acts
    "chutiya", "chutiye", "chutmar", "chutiyapa", "choot", "chut", "chute", "chutmarike", "takke",
    "laude", "laudey", "laura", "lauda", "loda", "lode", "lund", "lavda", "lawda", "lundwa", "lora", "ling",
    "gandu", "gaandu", "gand", "gaand", "gandfat", "gandfut", "gandiya", "gandiye", "gandphatu", "gandphati", 
    "gandphata", "gandphaton", "gaandmasti", "gandmarna", "gandmaru", "gandmarana", "gandmari", "gandmari ke", "land marike",
    "chod", "chodd", "chodna", "chudna", "chud", "chodo", "chodi", "chodne", "chudne", "chudney", "chodai", "chudai", 
    "chudwa", "chudwaa", "chudwane", "chudwaane", "chudvana", "chodu", "chodela",
    "tatte", "tatti", "tatty", "gote", "gotey", "gotte",
    "hijda", "hijra", "hijade", "chakka", "faggot",
    "babbe", "babbey", "chooche", "choochi", "chuchi", "mamme", "mammey", "bube", "bubey", "boobley", "buuble", "baable", "chuchiyan",
    "muth", "mooth", "muthi", "mutthal", "muth marna", "muthmarna",
    "lulli", "nunni", "nunnu", "bund"
}

LEVEL_1_MILD = {
    # Animals / Mild insults / Stupidity / Excrements
    "kutta", "kutte", "kuttey", "kutia", "kutiya", "kuttiya", "kutti", "suar", "pig",
    "gadha", "gadhe", "ullu", "harami", "haramia", "haramzada", "haramzadi", "haramkhor", "haraamkhor",
    "kamina", "kamini", "bevda", "bewda", "bevdey", "bewday", "bevakoof", "bevkoof", "bevkuf", "bewakoof", "bewkoof", "bewkuf",
    "fattu", "dalaal", "dalal", "dalle", "dalley", "jhat", "jhaat", "jhaatu", "jhatu", "landi", "landy",
    "moot", "mut", "mootne", "mutne", "mooth", "pesaab", "pesab", "peshaab", "peshab", "pisaab", "pisab",
    "pilla", "pillay", "pille", "pilley", "paji", "paaji", "hag", "haggu", "hagne", "hagney", "bakchod", "bakchodd", "bakchodi",
    "suar ki aulad", "suar ki zat", "kutte ki zat", "gadhe ki aulad", "gadhe ki zat", "bandar ki aulad",
    "bandar ki zat", "bhains ki aulad", "bhains ki zat", "ullu ki aulad", "ullu ki zat", "lomdi ki aulad",
    "lomdi ki zat", "bhed ki aulad", "bhed ki zat", "bakri ki aulad", "bakri ki zat", "billi ki aulad",
    "billi ki zat", "mendhak ki aulad", "mendhak ki zat", "badir", "badirchand", "bakland", "bhandi"
}

def collapse_duplicates(text: str) -> str:
    """
    Collapses consecutive duplicate letters into a single letter.
    e.g., 'maaaaadarchooooodddd' -> 'madarchod'
    """
    if not text:
        return ""
    # Collapses consecutive repeats of any character (case-insensitive conversion handled outside)
    return re.sub(r'(.)\1+', r'\1', text)

def reconstruct_spaced_words(text: str) -> list:
    """
    Groups consecutive tokens of length <= 2 to reconstruct words written with newlines or spaces.
    e.g., ['g', 'a', 'n', 'd', 'u'] -> ['gandu']
    e.g., ['tu', 'm', 'c'] -> ['tumc']
    """
    tokens = text.split()
    reconstructed = []
    current_word = []
    
    for t in tokens:
        # Strip symbols from individual token to assess its true character length
        clean_token = re.sub(r'[\.\-\_\,\*\#\@\!\$\%\^\&\(\)\=\+]', '', t)
        if len(clean_token) <= 2:
            current_word.append(clean_token)
        else:
            if current_word:
                reconstructed.append("".join(current_word))
                current_word = []
            reconstructed.append(clean_token)
            
    if current_word:
        reconstructed.append("".join(current_word))
        
    return reconstructed

def clean_and_normalize(text: str) -> str:
    """
    Cleans punctuation, collapses consecutive spaces and duplicate letters.
    """
    # 1. Lowercase
    text = text.lower()
    # 2. Strip dots, hyphens, symbols that try to mask the word, e.g. b.s.d.k -> bsdk
    text = re.sub(r'[\.\-\_\,\*\#\@\!\$\%\^\&\(\)\=\+]', '', text)
    # 3. Collapse duplicate letters
    text = collapse_duplicates(text)
    return text

# Whitelist of clean Hinglish/English words containing slang substrings.
# These will be replaced in the fully compressed message before checking for slangs.
CLEAN_WORDS_WHITELIST = {
    "sugandh", "sugand", "gandhi", "gandh", "gandhar", "gandharva", "gandak", "gandmool",
    "blunder", "plunder", "flounder", "grand", "brand", "random", "memorandum", 
    "bichhod", "chutney", "laudable", "applaud"
}

# Pre-collapse dictionaries for fast matching
COLLAPSED_LEVEL_3 = {collapse_duplicates(word) for word in LEVEL_3_EXTREME}
COLLAPSED_LEVEL_2 = {collapse_duplicates(word) for word in LEVEL_2_INSULTS}
COLLAPSED_LEVEL_1 = {collapse_duplicates(word) for word in LEVEL_1_MILD}

def analyze_message_slangs(message_text: str) -> dict:
    """
    Analyzes the message text to detect any Hinglish/Hindi slangs.
    Handles standard text, spaced-out characters, and vertical messages with newlines.
    Returns a dict specifying if slang was detected and the highest level found.
    """
    if not message_text:
        return {"detected": False, "level": 0, "matched_words": []}

    # Normalize case and strip symbols first
    clean_msg = message_text.lower()
    
    # Reconstruct any spaced-out or vertical characters (length <= 2 grouped)
    reconstructed_words = reconstruct_spaced_words(clean_msg)
    
    # Process each reconstructed word: collapse duplicates
    normalized_words = [collapse_duplicates(w) for w in reconstructed_words]

    matched_words = []
    highest_level = 0

    # 1. Strict exact check for reconstructed words.
    # This matches short acronyms (like 'mc', 'bc') correctly when written spaced-out,
    # but prevents false positives like 'webcam' or 'broadcast'.
    for word in normalized_words:
        if word in COLLAPSED_LEVEL_3:
            matched_words.append(word)
            highest_level = max(highest_level, 3)
        elif word in COLLAPSED_LEVEL_2:
            matched_words.append(word)
            highest_level = max(highest_level, 2)
        elif word in COLLAPSED_LEVEL_1:
            matched_words.append(word)
            highest_level = max(highest_level, 1)

    # 2. Substring matching on the compressed string.
    # To catch obfuscation (like 'gan\nd\nu'), we collapse all duplicate letters,
    # remove all whitespaces (spaces, newlines, tabs), mask clean words, and check.
    full_collapsed = collapse_duplicates(clean_and_normalize(message_text))
    full_collapsed_no_spaces = re.sub(r'\s+', '', full_collapsed)

    # Clean Word Masking: Replace collapsed clean words from the whitelist to prevent false matches
    sorted_whitelist = sorted(CLEAN_WORDS_WHITELIST, key=len, reverse=True)
    for clean_word in sorted_whitelist:
        collapsed_clean = collapse_duplicates(clean_word.lower().replace(" ", ""))
        full_collapsed_no_spaces = full_collapsed_no_spaces.replace(collapsed_clean, "CLEAN")

    # Check Level 3 phrases/words (only if length >= 3 to avoid matching 'mc' / 'bc' as sub-parts)
    for word in LEVEL_3_EXTREME:
        collapsed_phrase = collapse_duplicates(word.lower().replace(" ", ""))
        if len(collapsed_phrase) >= 3 and collapsed_phrase in full_collapsed_no_spaces:
            if collapsed_phrase not in matched_words:
                matched_words.append(word)
                highest_level = max(highest_level, 3)

    # Check Level 2 phrases/words (only if length >= 3)
    for word in LEVEL_2_INSULTS:
        collapsed_phrase = collapse_duplicates(word.lower().replace(" ", ""))
        if len(collapsed_phrase) >= 3 and collapsed_phrase in full_collapsed_no_spaces:
            if collapsed_phrase not in matched_words:
                matched_words.append(word)
                highest_level = max(highest_level, 2)

    # Check Level 1 phrases/words (only if length >= 3)
    for word in LEVEL_1_MILD:
        collapsed_phrase = collapse_duplicates(word.lower().replace(" ", ""))
        if len(collapsed_phrase) >= 3 and collapsed_phrase in full_collapsed_no_spaces:
            if collapsed_phrase not in matched_words:
                matched_words.append(word)
                highest_level = max(highest_level, 1)

    return {
        "detected": highest_level > 0,
        "level": highest_level,
        "matched_words": list(set(matched_words)) # Unique elements
    }
