"""
Tarefa Service - Business Logic
"""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from aws_lambda_powertools import Logger
from models import Tarefa, StatusTarefa
from schemas import TarefaCreate, TarefaUpdate, TarefaResponse
from utils.exceptions import NotFoundException, ForbiddenException

logger = Logger(child=True)


class TarefaService:
    """Tarefa business logic"""
    
    @staticmethod
    def create_tarefa(db: Session, data: TarefaCreate, usuario_id: str) -> TarefaResponse:
        """
        Create new tarefa
        
        Args:
            db: Database session
            data: Tarefa creation data
            usuario_id: ID of the user creating the tarefa
        
        Returns:
            Created tarefa
        """
        tarefa = Tarefa(
            titulo=data.titulo,
            descricao=data.descricao,
            criado_por=usuario_id,
            atualizado_por=usuario_id
        )
        
        db.add(tarefa)
        db.flush()
        
        logger.info(f"Tarefa created: {tarefa.id} by user {usuario_id}")
        return TarefaResponse.model_validate(tarefa)
    
    @staticmethod
    def list_tarefas(
        db: Session,
        usuario_id: str,
        status: Optional[StatusTarefa] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[TarefaResponse]:
        """
        List tarefas for a user
        
        Args:
            db: Database session
            usuario_id: User ID
            status: Filter by status (optional)
            limit: Maximum number of results
            offset: Pagination offset
        
        Returns:
            List of tarefas
        """
        query = db.query(Tarefa).filter(Tarefa.criado_por == usuario_id)
        
        if status:
            query = query.filter(Tarefa.status == status)
        
        tarefas = query.order_by(Tarefa.data_criacao.desc()).limit(limit).offset(offset).all()
        
        logger.info(f"Listed {len(tarefas)} tarefas for user {usuario_id}")
        return [TarefaResponse.model_validate(t) for t in tarefas]
    
    @staticmethod
    def get_tarefa_by_id(db: Session, tarefa_id: str, usuario_id: str) -> TarefaResponse:
        """
        Get tarefa by ID
        
        Args:
            db: Database session
            tarefa_id: Tarefa ID
            usuario_id: User ID (for authorization)
        
        Returns:
            Tarefa data
        
        Raises:
            NotFoundException: If tarefa not found
            ForbiddenException: If user doesn't own the tarefa
        """
        tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
        
        if not tarefa:
            logger.warning(f"Tarefa not found: {tarefa_id}")
            raise NotFoundException("Tarefa não encontrada")
        
        if tarefa.criado_por != usuario_id:
            logger.warning(f"User {usuario_id} tried to access tarefa {tarefa_id} owned by {tarefa.criado_por}")
            raise ForbiddenException("Você não tem permissão para acessar esta tarefa")
        
        return TarefaResponse.model_validate(tarefa)
    
    @staticmethod
    def update_tarefa(
        db: Session,
        tarefa_id: str,
        data: TarefaUpdate,
        usuario_id: str
    ) -> TarefaResponse:
        """
        Update tarefa
        
        Args:
            db: Database session
            tarefa_id: Tarefa ID
            data: Update data
            usuario_id: User ID (for authorization)
        
        Returns:
            Updated tarefa
        
        Raises:
            NotFoundException: If tarefa not found
            ForbiddenException: If user doesn't own the tarefa
        """
        tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
        
        if not tarefa:
            logger.warning(f"Tarefa not found: {tarefa_id}")
            raise NotFoundException("Tarefa não encontrada")
        
        if tarefa.criado_por != usuario_id:
            logger.warning(f"User {usuario_id} tried to update tarefa {tarefa_id} owned by {tarefa.criado_por}")
            raise ForbiddenException("Você não tem permissão para atualizar esta tarefa")
        
        # Update fields
        if data.titulo is not None:
            tarefa.titulo = data.titulo
        
        if data.descricao is not None:
            tarefa.descricao = data.descricao
        
        if data.status is not None:
            tarefa.status = data.status
            
            # Set data_conclusao if status is CONCLUIDA
            if data.status == StatusTarefa.CONCLUIDA and not tarefa.data_conclusao:
                tarefa.data_conclusao = datetime.utcnow()
        
        tarefa.atualizado_por = usuario_id
        
        db.flush()
        
        logger.info(f"Tarefa updated: {tarefa_id} by user {usuario_id}")
        return TarefaResponse.model_validate(tarefa)
    
    @staticmethod
    def delete_tarefa(db: Session, tarefa_id: str, usuario_id: str) -> None:
        """
        Delete tarefa
        
        Args:
            db: Database session
            tarefa_id: Tarefa ID
            usuario_id: User ID (for authorization)
        
        Raises:
            NotFoundException: If tarefa not found
            ForbiddenException: If user doesn't own the tarefa
        """
        tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
        
        if not tarefa:
            logger.warning(f"Tarefa not found: {tarefa_id}")
            raise NotFoundException("Tarefa não encontrada")
        
        if tarefa.criado_por != usuario_id:
            logger.warning(f"User {usuario_id} tried to delete tarefa {tarefa_id} owned by {tarefa.criado_por}")
            raise ForbiddenException("Você não tem permissão para deletar esta tarefa")
        
        db.delete(tarefa)
        
        logger.info(f"Tarefa deleted: {tarefa_id} by user {usuario_id}")