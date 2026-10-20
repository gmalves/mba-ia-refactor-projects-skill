"""Serviço de notificação (stub explícito).

Envia e-mail de verdade apenas quando SMTP_USER/SMTP_PASSWORD forem fornecidos
via ambiente; caso contrário, registra a notificação em log. Nenhuma credencial
fica hardcoded.
"""
import logging
import smtplib

from config.settings import Config

logger = logging.getLogger(__name__)


class NotificationService:
    def send_email(self, to, subject, body):
        if not Config.SMTP_USER or not Config.SMTP_PASSWORD:
            logger.info(
                "Notificação (stub): SMTP não configurado; e-mail não enviado para %s (%s)",
                to,
                subject,
            )
            return False

        try:
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                server.sendmail(
                    Config.SMTP_USER, to, f"Subject: {subject}\n\n{body}"
                )
            logger.info("E-mail enviado para %s", to)
            return True
        except Exception as exc:
            logger.warning("Falha ao enviar e-mail para %s: %s", to, exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)
