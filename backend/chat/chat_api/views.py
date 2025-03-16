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
import os
from .models import Document, Chat, Message
from .serializers import DocumentSerializer, ChatSerializer, MessageSerializer


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

        # Create embeddings and store in FAISS
        embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        vectorstore = FAISS.from_texts(texts, embeddings)

        # Save vectorstore path or handle storage as needed
        document.vectorstore_path = f"vectorstores/{document.id}"
        document.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    def create(self, request, *args, **kwargs):
        # Add a default title if not provided
        if 'title' not in request.data:
            request.data['title'] = f"New Chat {Chat.objects.count() + 1}"
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        chat = self.get_object()
        user_message = request.data.get('message')

        if not user_message:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create user message
        Message.objects.create(
            chat=chat,
            content=user_message,
            is_user=True
        )

        # Get relevant documents using RAG
        documents = Document.objects.all()
        if not documents.exists():
            return Response(
                {"error": "No documents available for context"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Initialize RAG components
            embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
            vectorstore = FAISS.from_texts(
                [doc.content for doc in documents],
                embeddings
            )

            llm = ChatOpenAI(
                temperature=0,
                openai_api_key=settings.OPENAI_API_KEY,
                model_name="gpt-3.5-turbo"
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

            # Get response
            result = chain({"question": user_message})
            assistant_message = result["answer"]

            # Create assistant message
            Message.objects.create(
                chat=chat,
                content=assistant_message,
                is_user=False
            )

            return Response({
                "message": assistant_message,
                "sources": [doc.page_content for doc in result["source_documents"]]
            })

        except Exception as e:
            return Response(
                {"error": f"Error processing message: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )