"""
Authentication routes for LandPPT
"""

from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import logging

from .auth_service import get_auth_service, AuthService
from .middleware import get_current_user_optional, get_current_user_required, get_current_user
from ..database.database import get_db
from ..database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="src/landppt/web/templates")


@router.get("/auth/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    error: str = None,
    success: str = None,
    username: str = None
):
    """Login page"""
    # Check if user is already logged in using request.state.user set by middleware
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/landppt/dashboard", status_code=302)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "success": success,
        "username": username
    })


@router.post("/auth/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle login form submission"""
    try:
        # Authenticate user
        user = auth_service.authenticate_user(db, username, password)
        
        if not user:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "error": "用户名或密码错误",
                "username": username
            })
        
        # Create session
        session_id = auth_service.create_session(db, user)
        
        # Redirect to dashboard
        response = RedirectResponse(url="/landppt/dashboard", status_code=302)

        # Set cookie max_age based on session expiration
        # If session_expire_minutes is 0, set cookie to never expire (None means session cookie)
        current_expire_minutes = auth_service._get_current_expire_minutes()
        cookie_max_age = None if current_expire_minutes == 0 else current_expire_minutes * 60

        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=cookie_max_age,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        logger.info(f"User {username} logged in successfully")
        return response
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "登录过程中发生错误，请重试",
            "username": username
        })


@router.get("/auth/logout")
async def logout(
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Logout user"""
    session_id = request.cookies.get("session_id")
    
    if session_id:
        auth_service.logout_user(db, session_id)
    
    response = RedirectResponse(url="/landppt/auth/login?success=已成功退出登录", status_code=302)
    response.delete_cookie("session_id")
    
    return response


@router.get("/auth/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    user: User = Depends(get_current_user_required)
):
    """User profile page"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user.to_dict()
    })


@router.post("/auth/change-password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Change user password"""
    try:
        # Validate current password
        if not user.check_password(current_password):
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user.to_dict(),
                "error": "当前密码错误"
            })
        
        # Validate new password
        if new_password != confirm_password:
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user.to_dict(),
                "error": "新密码和确认密码不匹配"
            })
        
        if len(new_password) < 6:
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user.to_dict(),
                "error": "密码长度至少6位"
            })
        
        # Update password
        if auth_service.update_user_password(db, user, new_password):
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user.to_dict(),
                "success": "密码修改成功"
            })
        else:
            return templates.TemplateResponse("profile.html", {
                "request": request,
                "user": user.to_dict(),
                "error": "密码修改失败，请重试"
            })
            
    except Exception as e:
        logger.error(f"Change password error: {e}")
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "user": user.to_dict(),
            "error": "修改密码过程中发生错误"
        })


@router.post("/api/auth/register")
async def api_register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(None),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """API用户注册端点 - 注册成功返回302，失败返回200"""
    logger.info(f"收到注册请求 - 用户名: {username}, 邮箱: {email}")
    
    try:
        # 检查数据库连接状态
        if not db:
            logger.error("数据库会话无效")
            return {
                "success": False,
                "message": "数据库连接失败",
                "user": None
            }
        
        # 记录注册前的数据库状态
        user_count_before = db.query(User).count()
        logger.info(f"注册前用户总数: {user_count_before}")
        
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            logger.warning(f"用户名已存在: {username}")
            return {
                "success": False,
                "message": "用户名已存在",
                "user": None
            }
        
        # 调用注册服务
        logger.info(f"开始注册用户: {username}")
        result = auth_service.register_user(db, username, password, email)
        
        if result["success"]:
            # 注册成功，双重验证用户是否真的在数据库中
            user = result["user"]
            logger.info(f"注册服务返回成功 - 用户ID: {user.id}, 用户名: {user.username}")
            
            # 验证用户是否真的存在
            verify_user = db.query(User).filter(User.username == username).first()
            if not verify_user:
                logger.error(f"用户注册验证失败 - 用户不存在于数据库: {username}")
                return {
                    "success": False,
                    "message": "注册验证失败，请重试",
                    "user": None
                }
            
            # 记录注册后的数据库状态
            user_count_after = db.query(User).count()
            logger.info(f"注册后用户总数: {user_count_after}")
            
            # 验证用户ID一致性
            if user.id != verify_user.id:
                logger.error(f"用户ID不一致 - 注册服务返回ID: {user.id}, 数据库查询ID: {verify_user.id}")
                return {
                    "success": False,
                    "message": "注册验证失败，用户ID不一致",
                    "user": None
                }
            
            # 创建会话
            session_id = None
            try:
                session_id = auth_service.create_session(db, user)
                logger.info(f"用户会话创建成功 - 会话ID: {session_id[:10]}...")
            except Exception as session_error:
                logger.error(f"创建用户会话失败: {session_error}")
                # 即使会话创建失败，用户已经注册成功，仍然返回成功
                # 但记录错误日志
            
            # 返回302重定向响应
            response = RedirectResponse(url="/landppt/dashboard", status_code=302)
            
            # 设置cookie
            current_expire_minutes = auth_service._get_current_expire_minutes()
            cookie_max_age = None if current_expire_minutes == 0 else current_expire_minutes * 60
            
            if session_id:
                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    max_age=cookie_max_age,
                    httponly=True,
                    secure=False,
                    samesite="lax"
                )
                logger.info(f"设置用户Cookie成功 - 用户名: {username}")
            
            logger.info(f"用户注册完成 - 用户名: {username} (ID: {user.id})")
            return response
        else:
            # 注册失败，返回200状态码和错误信息
            logger.warning(f"用户注册失败 - 用户名: {username}, 原因: {result['message']}")
            return {
                "success": False,
                "message": result["message"],
                "user": None
            }
            
    except Exception as e:
        logger.error(f"API registration error: {e}", exc_info=True)
        # 注册失败，返回200状态码和错误信息
        return {
            "success": False,
            "message": f"注册失败: {str(e)}",
            "user": None
        }


# API endpoints for authentication
@router.post("/api/auth/login")
async def api_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """API login endpoint - 登录成功返回302，失败返回200并提供信息"""
    logger.info(f"收到API登录请求 - 用户名: {username}")
    
    try:
        # 验证用户
        user = auth_service.authenticate_user(db, username, password)
        
        if not user:
            logger.warning(f"API登录失败 - 用户名或密码错误: {username}")
            # 登录失败返回200状态码和错误信息
            return {
                "success": False,
                "message": "用户名或密码错误",
                "user": None
            }
        
        logger.info(f"API登录验证成功 - 用户名: {username} (ID: {user.id})")
        
        # 创建会话
        session_id = auth_service.create_session(db, user)
        logger.info(f"API登录会话创建成功 - 用户名: {username}, 会话ID: {session_id[:10]}...")
        
        # 登录成功返回302重定向
        response = RedirectResponse(url="/landppt/dashboard", status_code=302)
        
        # 设置cookie
        current_expire_minutes = auth_service._get_current_expire_minutes()
        cookie_max_age = None if current_expire_minutes == 0 else current_expire_minutes * 60
        
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=cookie_max_age,
            httponly=True,
            secure=False,  # 生产环境使用HTTPS时设置为True
            samesite="lax"
        )
        
        logger.info(f"API登录成功完成 - 用户名: {username}")
        return response
        
    except Exception as e:
        logger.error(f"API登录异常 - 用户名: {username}, 错误: {e}", exc_info=True)
        # 异常时也返回200状态码和错误信息
        return {
            "success": False,
            "message": f"登录过程中发生错误: {str(e)}",
            "user": None
        }


@router.post("/api/auth/logout")
async def api_logout(
    request: Request,
    db: Session = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    """API logout endpoint"""
    session_id = request.cookies.get("session_id")
    
    if session_id:
        auth_service.logout_user(db, session_id)
    
    return {"success": True, "message": "已成功退出登录"}


@router.get("/api/auth/me")
async def api_current_user(
    user: User = Depends(get_current_user_required)
):
    """Get current user info"""
    return {
        "success": True,
        "user": user.to_dict()
    }


@router.get("/api/auth/check")
async def api_check_auth(
    request: Request,
    db: Session = Depends(get_db)
):
    """Check authentication status"""
    user = get_current_user_optional(request, db)
    
    return {
        "authenticated": user is not None,
        "user": user.to_dict() if user else None
    }
