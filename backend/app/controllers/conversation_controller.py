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

    def get_recommendations_by_jlpt(self, conversation_id: str) -> list[dict]:
        conversation = self.conversation_repo.find_by_id(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        category_id = self._map_jlpt_to_category(conversation.jlpt_target or conversation.level)
        if not category_id:
            return []

        try:
            resp = requests.get(
                self.course_service_base_url,
                params={"categoryId": category_id},
                timeout=5,
            )
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            return []

        courses = payload if isinstance(payload, list) else payload.get("data", [])

        recs = []
        for course in courses:
            recs.append({
                "type": "jlpt_course",
                "course_id": str(course.get("id", "")),
                "title": course.get("title") or course.get("name"),
                "category_id": category_id,
                "reason": f"Recommended for JLPT {conversation.jlpt_target or conversation.level}"
            })
        return recs
