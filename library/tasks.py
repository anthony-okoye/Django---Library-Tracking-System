import logging
from django.utils import timezone
from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    today = timezone.localdate()
    overdue_loans = Loan.objects.select_related(
        'member__user', 'book'
    ).filter(
        is_returned=False,
        due_date__lt=today
    )

    set_count = 0
    
    for loan in overdue_loans:
        try:
            days_overdue = (today - loan.due_date).days
            send_mail(
                subject= f'Overdue: {loan.book.title}',
                message= (
                    f'Hello {loan.member.user.username},\n\nThis is a reminder that you have not returned "{loan.book.title}" on time.\n\n'
                    f'You are {days_overdue} days overdue.\n\n'
                    f'Please return the book as soon as possible.'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[loan.member.user.email],
                fail_silently=False,
            )
            sent_count = 1
            logger.info(f'Sent overdue notification for loan {loan.id}')
        except Exception as e:
            logger.error(f'Failed to send email for loan {loan.id}: {str(e)}')
            
    logger.info(f"overdue check complete. Sent {sent_count} notifications.")
    return sent_count