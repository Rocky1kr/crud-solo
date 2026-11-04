from datetime import datetime

from fastapi import FastAPI, Form, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 날짜 표시용 필터: 템플릿에서 {{ post.created_at | dt }} 로 사용
templates.env.filters["dt"] = lambda d: d.strftime("%Y.%m.%d %H:%M")

TITLE_MAX = 100

# ── 가상 DB (메모리) ────────────────────────────────────────
# 서버가 재시작되면 초기화됩니다.
posts: dict[int, dict] = {}
next_id = 1  # 삭제해도 번호가 재사용되지 않도록 따로 관리


def add_post(title: str, content: str) -> dict:
    global next_id
    post = {
        "id": next_id,
        "title": title,
        "content": content,
        "created_at": datetime.now(),
        "updated_at": None,
    }
    posts[next_id] = post
    next_id += 1
    return post


def get_post_or_404(post_id: int) -> dict:
    post = posts.get(post_id)
    if post is None:
        raise HTTPException(status_code=404)
    return post


def validate(title: str, content: str) -> str | None:
    """문제가 있으면 오류 메시지, 없으면 None"""
    if not title:
        return "제목을 입력해 주세요."
    if len(title) > TITLE_MAX:
        return f"제목은 {TITLE_MAX}자 이내로 입력해 주세요."
    if not content:
        return "내용을 입력해 주세요."
    return None


add_post("게시판을 열었습니다", "자유롭게 글을 남겨 주세요.\n수정과 삭제도 할 수 있어요.")
add_post("오늘 점심 뭐 먹지", "김치찌개 vs 돈까스\n의견 받습니다.")


# ── 404 페이지 ──────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def not_found_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            request=request, name="404.html", status_code=404
        )
    return await http_exception_handler(request, exc)


# ── 라우트 ──────────────────────────────────────────────────
@app.get("/")
def home():
    return RedirectResponse("/posts")


# 목록 (검색: /posts?q=점심)
@app.get("/posts")
def post_list(request: Request, q: str = ""):
    q = q.strip()
    items = sorted(posts.values(), key=lambda p: p["id"], reverse=True)
    if q:
        items = [
            p for p in items
            if q.lower() in p["title"].lower() or q.lower() in p["content"].lower()
        ]
    return templates.TemplateResponse(
        request=request,
        name="list.html",
        context={"posts": items, "q": q, "total": len(posts)},
    )


# 작성 폼
@app.get("/posts/new")
def post_new(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="form.html",
        context={"mode": "new", "post": {"title": "", "content": ""}},
    )


# 작성 처리
@app.post("/posts/create")
def post_create(request: Request, title: str = Form(""), content: str = Form("")):
    title, content = title.strip(), content.strip()
    error = validate(title, content)
    if error:
        return templates.TemplateResponse(
            request=request,
            name="form.html",
            context={"mode": "new", "post": {"title": title, "content": content}, "error": error},
            status_code=400,
        )
    post = add_post(title, content)
    return RedirectResponse(f"/posts/{post['id']}", status_code=303)


# 상세
@app.get("/posts/{post_id}")
def post_detail(request: Request, post_id: int):
    post = get_post_or_404(post_id)
    return templates.TemplateResponse(
        request=request, name="detail.html", context={"post": post}
    )


# 수정 폼
@app.get("/posts/{post_id}/edit")
def post_edit(request: Request, post_id: int):
    post = get_post_or_404(post_id)
    return templates.TemplateResponse(
        request=request, name="form.html", context={"mode": "edit", "post": post}
    )


# 수정 처리
@app.post("/posts/{post_id}/update")
def post_update(
    request: Request, post_id: int, title: str = Form(""), content: str = Form("")
):
    post = get_post_or_404(post_id)
    title, content = title.strip(), content.strip()
    error = validate(title, content)
    if error:
        draft = {**post, "title": title, "content": content}
        return templates.TemplateResponse(
            request=request,
            name="form.html",
            context={"mode": "edit", "post": draft, "error": error},
            status_code=400,
        )
    post["title"] = title
    post["content"] = content
    post["updated_at"] = datetime.now()
    return RedirectResponse(f"/posts/{post_id}", status_code=303)


# 삭제
@app.post("/posts/{post_id}/delete")
def post_delete(post_id: int):
    get_post_or_404(post_id)
    posts.pop(post_id)
    return RedirectResponse("/posts", status_code=303)
