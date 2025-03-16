from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage
import os
import logging
from .models import Document, Chat, Message
from .serializers import DocumentSerializer, ChatSerializer, MessageSerializer

logger = logging.getLogger(__name__)

class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Process document for RAG
        document = serializer.instance
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        texts = text_splitter.split_text(document.content)

        try:
            # Create embeddings and store in FAISS
            embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model="text-embedding-ada-002"
            )
            vectorstore = FAISS.from_texts(texts, embeddings)

            # Save vectorstore path or handle storage as needed
            document.vectorstore_path = f"vectorstores/{document.id}"
            document.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return Response(
                {"error": f"Error processing document: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        if 'title' not in data:
            data['title'] = f"New Chat {Chat.objects.count() + 1}"
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='send_message', url_name='send_message')
    def send_message(self, request, pk=None):
        try:
            chat = self.get_object()
            user_message = request.data.get('message')

            if not user_message:
                return Response(
                    {"error": "Message content is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create user message
            user_msg = Message.objects.create(
                chat=chat,
                content=user_message,
                is_user=True
            )

            try:
                # Initialize OpenAI components with minimal configuration
                llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.7,
                    api_key=settings.OPENAI_API_KEY
                )

                # Get relevant documents using RAG if they exist
                documents = Document.objects.all()
                if documents.exists():
                    try:
                        # Initialize RAG components
                        embeddings = OpenAIEmbeddings(
                            openai_api_key=settings.OPENAI_API_KEY,
                            model="text-embedding-ada-002"
                        )
                        
                        vectorstore = FAISS.from_texts(
                            [doc.content for doc in documents],
                            embeddings
                        )

                        memory = ConversationBufferMemory(
                            memory_key="chat_history",
                            return_messages=True
                        )

                        chain = ConversationalRetrievalChain.from_llm(
                            llm=llm,
                            retriever=vectorstore.as_retriever(),
                            memory=memory,
                            return_source_documents=True
                        )

                        # Get response with context
                        result = chain({"question": user_message})
                        assistant_message = result["answer"]
                        sources = [doc.page_content for doc in result["source_documents"]]
                    except Exception as e:
                        logger.error(f"Error with RAG processing: {str(e)}")
                        # Fallback to regular chat if RAG fails
                        response = llm([HumanMessage(content=user_message)])
                        assistant_message = response.content
                        sources = []
                else:
                    # If no documents, just use the base model
                    response = llm([HumanMessage(content=user_message)])
                    assistant_message = response.content
                    sources = []

                # Create assistant message
                assistant_msg = Message.objects.create(
                    chat=chat,
                    content=assistant_message,
                    is_user=False
                )

                return Response({
                    "user_message": MessageSerializer(user_msg).data,
                    "assistant_message": MessageSerializer(assistant_msg).data,
                    "sources": sources
                })

            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Delete the user message if assistant message fails
                user_msg.delete()
                return Response(
                    {"error": f"Error processing message: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Chat.DoesNotExist:
            return Response(
                {"error": "Chat not found"},
                status=status.HTTP_404_NOT_FOUND
            )