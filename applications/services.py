"""
applications/services.py

Pipeline xử lý CV và chấm điểm CV-JD bằng TF-IDF + Cosine Similarity.

SubTask 6.1  : extract_text_from_pdf()  — pdfminer.six only, không dùng PyPDF2
SubTask 6.2  : extract_text_from_docx() — python-docx
SubTask 6.3  : preprocess_text()        — chuẩn hóa, lowercase, loại ký tự đặc biệt
SubTask 6.4+6.6: score_applications_for_job() — 1 TfidfVectorizer / corpus / JobPost
SubTask 6.5  : process_cv_and_score()   — pipeline đầy đủ cho 1 Application mới
               → similarity_score = NULL khi lỗi (KHÔNG gán 0)

Quy tắc bất biến:
  • MIN_TEXT_LENGTH = 100 ký tự sau tiền xử lý → INSUFFICIENT_TEXT
  • Khi lỗi: scoring_status = EXTRACTION_FAILED / INSUFFICIENT_TEXT / SCORING_FAILED,
    similarity_score = NULL, ranking_position = NULL
  • Cập nhật score qua Application.objects.filter().update() để tránh trigger
    full_clean() constraint (application_score_only_when_scored).
"""

import logging
import re

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────
# Hằng số
# ────────────────────────────────────────────────────────────────────────────
MIN_TEXT_LENGTH = 100  # ký tự sau tiền xử lý; ít hơn → INSUFFICIENT_TEXT


# ════════════════════════════════════════════════════════════════════════════
# SubTask 6.3 — Tiền xử lý văn bản
# ════════════════════════════════════════════════════════════════════════════

def preprocess_text(text: str) -> str:
    """
    Chuẩn hóa văn bản trước khi đưa vào TF-IDF:
      1. Lowercase
      2. Loại bỏ ký tự đặc biệt (giữ chữ cái, số, khoảng trắng)
      3. Thu gọn khoảng trắng thừa
      4. Strip đầu/cuối
    """
    if not text:
        return ""
    text = text.lower()
    # Giữ lại chữ cái (bao gồm Unicode tiếng Việt), số, khoảng trắng
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ════════════════════════════════════════════════════════════════════════════
# SubTask 6.1 — Trích xuất văn bản từ PDF (pdfminer.six)
# ════════════════════════════════════════════════════════════════════════════

def extract_text_from_pdf(file_path: str) -> str:
    """
    Trích xuất văn bản từ tệp PDF bằng pdfminer.six.
    KHÔNG dùng PyPDF2.
    Trả về chuỗi văn bản thuần (chưa tiền xử lý).
    Raise Exception nếu lỗi.
    """
    from pdfminer.high_level import extract_text as pdfminer_extract

    text = pdfminer_extract(file_path)
    return text or ""


# ════════════════════════════════════════════════════════════════════════════
# SubTask 6.2 — Trích xuất văn bản từ DOCX (python-docx)
# ════════════════════════════════════════════════════════════════════════════

def extract_text_from_docx(file_path: str) -> str:
    """
    Trích xuất văn bản từ tệp DOCX bằng python-docx.
    Trả về chuỗi văn bản thuần (chưa tiền xử lý).
    Raise Exception nếu lỗi.
    """
    import docx

    doc = docx.Document(file_path)
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    # Bổ sung: lấy text từ bảng nếu có
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    paragraphs.append(cell_text)
    return "\n".join(paragraphs)


# ════════════════════════════════════════════════════════════════════════════
# Helper nội bộ — trích xuất text từ 1 Application
# ════════════════════════════════════════════════════════════════════════════

def _extract_cv_text(app) -> str:
    """
    Trích xuất text thô từ file CV của Application.
    Raise Exception với thông báo rõ ràng nếu lỗi.
    """
    import os

    if not app.cv_file:
        raise ValueError("Application không có cv_file.")

    file_path = app.cv_file.path
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Tệp CV không tìm thấy: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Định dạng tệp không hỗ trợ: {ext}")


# ════════════════════════════════════════════════════════════════════════════
# SubTask 6.5 — Xử lý 1 Application mới (pipeline đầy đủ)
# ════════════════════════════════════════════════════════════════════════════

def process_cv_and_score(application_id: int) -> None:
    """
    Pipeline đầy đủ cho 1 hồ sơ mới:
      1. Trích xuất text CV
      2. Tiền xử lý
      3. Kiểm tra độ dài tối thiểu
      4. Lưu cv_text vào Application
      5. Gọi score_applications_for_job() để tính lại toàn bộ corpus của JobPost đó

    Khi lỗi:
      - scoring_status = EXTRACTION_FAILED / INSUFFICIENT_TEXT / SCORING_FAILED
      - similarity_score = NULL, ranking_position = NULL
      - KHÔNG gán điểm 0
    """
    from applications.models import Application

    # Lấy Application — nếu không tồn tại thì log và return
    try:
        app = Application.objects.select_related("job_post").get(pk=application_id)
    except Application.DoesNotExist:
        logger.error("process_cv_and_score: Application id=%s không tồn tại.", application_id)
        return

    # ── Bước 1: Trích xuất text ──────────────────────────────────────────
    try:
        raw_text = _extract_cv_text(app)
    except Exception as exc:
        logger.warning(
            "Trích xuất CV thất bại [app=%s]: %s", application_id, exc
        )
        Application.objects.filter(pk=application_id).update(
            scoring_status=Application.ScoringStatus.EXTRACTION_FAILED,
            cv_text=None,
            similarity_score=None,
            ranking_position=None,
        )
        return

    # ── Bước 2: Tiền xử lý ──────────────────────────────────────────────
    processed = preprocess_text(raw_text)

    # ── Bước 3: Kiểm tra độ dài ─────────────────────────────────────────
    if len(processed) < MIN_TEXT_LENGTH:
        logger.info(
            "CV quá ngắn [app=%s]: %d ký tự sau tiền xử lý.", application_id, len(processed)
        )
        Application.objects.filter(pk=application_id).update(
            scoring_status=Application.ScoringStatus.INSUFFICIENT_TEXT,
            cv_text=raw_text or None,   # lưu raw text để debug
            similarity_score=None,
            ranking_position=None,
        )
        return

    # ── Bước 4: Lưu cv_text ─────────────────────────────────────────────
    Application.objects.filter(pk=application_id).update(cv_text=raw_text)

    # ── Bước 5: Tính lại điểm toàn bộ corpus của JobPost ────────────────
    try:
        score_applications_for_job(app.job_post_id)
    except Exception as exc:
        logger.error(
            "score_applications_for_job thất bại [job=%s]: %s", app.job_post_id, exc
        )
        Application.objects.filter(pk=application_id).update(
            scoring_status=Application.ScoringStatus.SCORING_FAILED,
            similarity_score=None,
            ranking_position=None,
        )


# ════════════════════════════════════════════════════════════════════════════
# SubTask 6.4 + 6.6 — Tính điểm & thứ hạng cho toàn bộ corpus 1 JobPost
# ════════════════════════════════════════════════════════════════════════════

def score_applications_for_job(job_post_id: int) -> None:
    """
    Tính lại điểm phù hợp và thứ hạng cho tất cả hồ sơ hợp lệ của một JobPost.

    Corpus = [JD_text, CV_1, CV_2, ..., CV_n]
    → Fit 1 TfidfVectorizer trên toàn corpus
    → Tính cosine_similarity(JD_vector, CV_vector_i) cho từng CV

    Điều kiện hồ sơ hợp lệ tham gia corpus:
      - cv_text không null/rỗng
      - preprocess_text(cv_text) >= MIN_TEXT_LENGTH ký tự
      - scoring_status != EXTRACTION_FAILED (nghĩa là: đã có text)

    Hồ sơ không đủ điều kiện: giữ nguyên scoring_status (INSUFFICIENT_TEXT, EXTRACTION_FAILED,...)
    Khi lỗi tổng thể: đặt SCORING_FAILED cho hồ sơ đang PENDING, score = NULL
    KHÔNG bao giờ gán similarity_score = 0.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    from applications.models import Application
    from jobs.models import JobPost

    # ── Lấy JobPost ──────────────────────────────────────────────────────
    try:
        job = JobPost.objects.get(pk=job_post_id)
    except JobPost.DoesNotExist:
        logger.error("score_applications_for_job: JobPost id=%s không tồn tại.", job_post_id)
        return

    jd_raw = job.jd_text_source()
    jd_processed = preprocess_text(jd_raw)

    if len(jd_processed) < MIN_TEXT_LENGTH:
        logger.warning(
            "JD quá ngắn để chấm điểm [job=%s]: %d ký tự.", job_post_id, len(jd_processed)
        )
        return

    # ── Lấy tất cả Application của job (không lọc trạng thái hồ sơ) ─────
    all_apps = list(
        Application.objects.filter(job_post_id=job_post_id)
        .exclude(scoring_status=Application.ScoringStatus.EXTRACTION_FAILED)
        .values("id", "cv_text", "scoring_status")
    )

    # ── Phân loại hồ sơ ──────────────────────────────────────────────────
    valid_apps = []   # hồ sơ có đủ text để tham gia corpus
    for a in all_apps:
        raw = a["cv_text"] or ""
        processed = preprocess_text(raw)
        if len(processed) >= MIN_TEXT_LENGTH:
            valid_apps.append({"id": a["id"], "processed_text": processed})
        # Hồ sơ quá ngắn: đã được đặt INSUFFICIENT_TEXT ở process_cv_and_score
        # → không thay đổi ở đây

    if not valid_apps:
        logger.info(
            "Không có hồ sơ hợp lệ để chấm điểm [job=%s].", job_post_id
        )
        return

    # ── Xây dựng corpus: JD ở index 0, các CV tiếp theo ─────────────────
    corpus = [jd_processed] + [a["processed_text"] for a in valid_apps]

    # ── Fit TF-IDF trên toàn corpus ──────────────────────────────────────
    try:
        vectorizer = TfidfVectorizer(
            sublinear_tf=True,      # log(1+tf) — giảm ảnh hưởng tần số cao
            min_df=1,               # giữ cả từ chỉ xuất hiện 1 lần
            analyzer="word",
            token_pattern=r"(?u)\b\w+\b",
        )
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except Exception as exc:
        logger.error("TF-IDF fit thất bại [job=%s]: %s", job_post_id, exc)
        # Đặt SCORING_FAILED cho các hồ sơ đang PENDING
        pending_ids = [
            a["id"] for a in valid_apps
        ]
        Application.objects.filter(pk__in=pending_ids).update(
            scoring_status=Application.ScoringStatus.SCORING_FAILED,
            similarity_score=None,
            ranking_position=None,
        )
        return

    # ── Tính cosine similarity: JD vs từng CV ────────────────────────────
    jd_vector = tfidf_matrix[0]           # hàng 0 = JD
    cv_matrix = tfidf_matrix[1:]          # hàng 1..n = các CV

    similarities = cosine_similarity(jd_vector, cv_matrix).flatten()
    # similarities[i] ∈ [0.0, 1.0]

    # ── Tính ranking: thứ hạng 1 = điểm cao nhất ─────────────────────────
    # argsort tăng dần → đảo ngược để giảm dần
    sorted_indices = list(reversed(np.argsort(similarities).tolist()))
    ranks = {}
    for rank, idx in enumerate(sorted_indices, start=1):
        app_id = valid_apps[idx]["id"]
        ranks[app_id] = rank

    # ── Cập nhật DB — dùng .update() để tránh full_clean constraint ──────
    for i, a in enumerate(valid_apps):
        score = float(similarities[i])
        rank = ranks[a["id"]]
        Application.objects.filter(pk=a["id"]).update(
            scoring_status=Application.ScoringStatus.SCORED,
            similarity_score=round(score, 6),
            ranking_position=rank,
        )

    logger.info(
        "Chấm điểm hoàn tất [job=%s]: %d hồ sơ được chấm.", job_post_id, len(valid_apps)
    )
