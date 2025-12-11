# test_celery.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.celery_tasks import send_email_task

def test_celery():
    print("Testing Celery email task...")
    
    # Test 1: Check if task has .delay() method
    # print(f"Type of send_email_task: {type(send_email_task)}")
    # print(f"Has .delay() method: {hasattr(send_email_task, 'delay')}")
    # print(f"Methods available: {[m for m in dir(send_email_task) if not m.startswith('_')]}")
    
    # Test 2: Try to send a task
    try:
        # This should work with .delay()
        result = send_email_task.delay(
            link="http://example.com/verify/123",
            user_email="test@example.com",
            user_name="Test User",
            subject="Test Verification",
            tag="verification"
        )
        
        print(f"\n✅ Task submitted successfully!")
        print(f"Task ID: {result.id}")
        print(f"Task Status: {result.status}")
        
        # Optional: Wait for result (for testing only)
        print("Waiting for task to complete...")
        task_result = result.get(timeout=30)
        print(f"Task Result: {task_result}")
        
    except AttributeError as e:
        print(f"\n❌ AttributeError: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure @c_app.task decorator is applied to send_email_task")
        print("2. Check that c_app is properly initialized in config.py")
        print("3. Try using send_email_task.apply_async() instead")
        
        # Try alternative
        try:
            print("\nTrying apply_async...")
            result = send_email_task.apply_async(
                kwargs={
                    "link": "http://example.com/test",
                    "user_email": "test2@example.com",
                    "user_name": "Test User 2",
                    "subject": "Test",
                    "tag": "verification"
                }
            )
            print(f"apply_async worked! Task ID: {result.id}")
        except Exception as e2:
            print(f"apply_async also failed: {e2}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    test_celery()