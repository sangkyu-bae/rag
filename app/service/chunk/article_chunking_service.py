import re

ARTICLE_PATTERN = re.compile(r"제\s*\d+\s*조")
CLAUSE_PATTERN = re.compile(r"(\d+)\s*항")

class ArticleChunkingService:
    def __init__(
        self,
        doc:string
    ):

    def split_by_articles(text):
        parts = ARTICLE_PATTERN.split(text)
        articles = ARTICLE_PATTERN.findall(text)

        result = []
        for i, title in enumerate(articles):
            body = parts[i+1].strip()
            result.append((title, body))
        return result
    def tokenize_len(text):
    return len(tokenizer(text)["input_ids"])


    def split_article_into_clauses(article_title, article_body):
    # 항 split
    parts = CLAUSE_PATTERN.split(article_body)
    # CLAUSE_PATTERN.split → [before, 항번호1, 내용1, 항번호2, 내용2, ...]
    
    clauses = []
    i = 1
    while i < len(parts):
        clause_no = parts[i].strip()
        clause_body = parts[i+1].strip()
        clauses.append((clause_no, clause_body))
        i += 2
    
    # 항이 없는 문서 → 조 전체 처리
    if len(clauses) == 0:
        return [ (article_title, None, article_body) ]

    final_chunks = []

    for clause_no, body in clauses:
        t_len = tokenize_len(body)

        # 항이 너무 짧으면 조합해둘 용도로 표시
        if t_len < MIN_CLAUSE_TOKENS:
            final_chunks.append((article_title, clause_no, body, "short"))
        else:
            # 항이 너무 길면 내부 문단 기반 나누기
            paragraphs = body.split("\n\n")
            buffer = []
            for p in paragraphs:
                if tokenize_len("\n\n".join(buffer + [p])) > MAX_CHUNK_TOKENS:
                    final_chunks.append((article_title, clause_no, "\n\n".join(buffer), "normal"))
                    buffer = [p]
                else:
                    buffer.append(p)
            if buffer:
                final_chunks.append((article_title, clause_no, "\n\n".join(buffer), "normal"))

    return final_chunks
    
    def merge_short_clauses(clause_chunks):
        full_body = []
        final = []

        for title, clause_no, body, ctype in clause_chunks:
            full_body.append(f"{clause_no}항\n{body}\n")

            # short이면 조 전체 chunk로 merge 대상
        full_chunk = (title, None, "\n".join(full_body), "full")

        # normal chunk만 유지하고 short는 버리고 full chunk로 대체
        normal_chunks = [c for c in clause_chunks if c[3] == "normal"]

        return [full_chunk] + normal_chunks
    def create_summary(text, article_title):
        prompt = f"""
            다음은 {article_title}의 전체 내용입니다.
            핵심 내용을 150토큰 이내로 요약해주세요.

            내용:
            {text}
        """
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return res.choices[0].message.content
    def build_chunks_for_article(article_title, article_body):
        clause_chunks = split_article_into_clauses(article_title, article_body)
        merged = merge_short_clauses(clause_chunks)

        # full chunk는 title=None로 들어 있음
        full_chunk_text = [x for x in merged if x[3] == "full"][0][2]
        summary = create_summary(full_chunk_text, article_title)

        summary_chunk = (article_title, "summary", summary, "summary")

        return merged + [summary_chunk]

