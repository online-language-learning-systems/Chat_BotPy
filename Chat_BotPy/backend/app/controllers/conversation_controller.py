"""
Conversation Controller
Chỉ quản lý luồng điều khiển (flow) và tương tác giữa các service, repository
Logic nghiệp vụ được tách ra service riêng biệt
"""
from typing import Optional
from datetime import datetime
from app.models.conversation import Conversation, Message
from app.repositories.conversation_repository import ConversationRepository
from app.services.ai.base_ai_service import IAIService
from flask import request
from app.config import settings
import requests


class ConversationController:
    """
    Controller cho các thao tác liên quan đến Conversation.
    Dùng Dependency Injection nhận các repo và service,
    tập trung điều phối các bước xử lý, không xử lý logic nghiệp vụ.
    """

    def __init__(
            self,
            conversation_repo: ConversationRepository,
            ai_service: IAIService,
            course_service_base_url: str,
    ):
        self.conversation_repo = conversation_repo
        self.ai_service = ai_service
        self.course_service_base_url = course_service_base_url.rstrip('/')

    def create_conversation(
            self,
            user_id: str,
            topic: str,
            level: str
    ) -> Conversation:
        """
        Tạo mới một conversation

        Args:
            user_id: id người dùng
            topic: chủ đề hội thoại
            level: trình độ (N5-N1)

        Returns:
            Đối tượng Conversation mới tạo
        """
        # Tạo đối tượng Conversation mới
        conversation = Conversation(
            user_id=user_id,
            topic=topic,
            level=level
        )
        # Lưu vào repository (DB)
        return self.conversation_repo.create(conversation)

    def send_message(
            self,
            conversation_id: str,
            message_content: str,
            response_time: Optional[int] = None
    ) -> dict:
        """
        Nhận tin nhắn người dùng, xử lý phản hồi AI,
        cập nhật điểm số, lưu lại conversation

        Args:
            conversation_id: id conversation cần xử lý
            message_content: nội dung tin nhắn người dùng
            response_time: thời gian phản hồi (ms)

        Returns:
            Dict chứa user_message, ai_message và điểm tổng thể (overall_score)

        Raises:
            ValueError nếu không tìm thấy conversation
        """
        # Lấy conversation từ DB
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        if conversation.language != "ja":
            raise ValueError("Language not supported yet")

        # Tạo Message user
        user_message = Message(
            role='user',
            content=message_content,
            timestamp=datetime.utcnow(),
            analysis=None,
        )

        # Thêm message user vào conversation
        conversation.add_message(user_message)

        # Lấy lịch sử chat dưới dạng list dict (role, content) cho AI service
        chat_history = conversation.get_chat_history()
        ai_response = self.ai_service.chat(
            chat_history,
            conversation.topic,
            conversation.level
        )

        # Tạo Message AI
        ai_message = Message(
            role='assistant',
            content=ai_response,
            timestamp=datetime.utcnow()
        )
        # Thêm message AI vào conversation
        conversation.add_message(ai_message)

        # Lưu conversation đã cập nhật
        self.conversation_repo.update(conversation_id, conversation)

        # Trả dữ liệu cho API response
        return {
            'user_message': user_message.to_dict(),
            'ai_message': ai_message.to_dict(),
            'overall_score': conversation.overall_score.to_dict()
        }

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Lấy conversation theo id
        """
        return self.conversation_repo.find_by_id(conversation_id)

    def get_user_conversations(
            self,
            user_id: str,
            skip: int = 0,
            limit: int = 20
    ) -> list[Conversation]:
        """
        Lấy danh sách conversation của một user, có phân trang
        """
        return self.conversation_repo.find_by_user_id(user_id, skip, limit)

    def get_user_statistics(self, user_id: str) -> dict:
        """
        Lấy thống kê các cuộc hội thoại của người dùng

        Args:
            user_id: id người dùng

        Returns:
            Dict thống kê (tổng số conversation, điểm cuối cùng,...)
        """
        return self.conversation_repo.get_user_statistics(user_id)

    def _map_jlpt_to_category(self, jlpt_target: str) -> Optional[int]:
        mapping = {
            "N1": 1,
            "N2": 2,
            "N3": 3,
            "N4": 4,
            "N5": 5,
        }
        return mapping.get(jlpt_target)

    def _map_mode_to_tag(self, mode: str) -> Optional[int]:
        mapping = {
            "speaking_practice": 1,
            "listening_practice": 4,
            "grammar_practice": 2,
            "vocabulary_practice": 3,
        }
        return mapping.get(mode, 1)

    @staticmethod
    def _tag_label(tag_id: Optional[int]) -> Optional[str]:
        labels = {
            1: "Giao tiếp",
            2: "Ngữ pháp",
            3: "Từ vựng",
            4: "Luyện nghe",
        }
        return labels.get(tag_id) if tag_id else None

    def get_recommendations(self, conversation_id: str, auth_header: Optional[str] = None) -> list:
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        category_id = self._map_jlpt_to_category(conversation.jlpt_target or conversation.level)
        if not category_id:
            return []
        tag_id = self._map_mode_to_tag(conversation.conversation_mode)

        params = {
            "categoryId": category_id,
            "pageNo": 0,
            "pageSize": 6,
        }
        if tag_id:
            params["tagId"] = tag_id

        headers = {}
        if auth_header:
            headers["Authorization"] = auth_header

        url = f"{self.course_service_base_url.rstrip('/')}/storefront/courses"
        print(f"[course-service] Using base URL: {self.course_service_base_url}")
        try:
            resp = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=settings.COURSE_SERVICE_TIMEOUT,
            )
            print(f"[course-service] Request URL: {resp.url}")
            print(f"[course-service] Status code: {resp.status_code}")
            resp.raise_for_status()
            payload = resp.json()
            print(f"[course-service] Response body: {payload}")
        except Exception as e:
            print(f"[course-service] error: {e}")
            return []

        courses = payload if isinstance(payload, list) else payload.get("content") or payload.get("data") or []

        results = []
        for c in courses:
            c_tag = c.get("tagId") or c.get("tag_id")
            if tag_id and c_tag and c_tag != tag_id:
                continue
            results.append({
                "course_id": c.get("id") or c.get("courseId") or c.get("course_id"),
                "title": c.get("title") or c.get("courseTitle") or c.get("name"),
                "price": c.get("price"),
                "level": c.get("level"),
                "image_url": c.get("imagePresignedUrl") or c.get("image_url") or c.get("imageUrl"),
                "tag": self._tag_label(tag_id) if tag_id else self._tag_label(c_tag),
            })
        return results
