from src.db import get_db

def test_get_db_yields_session():
    # Retrieve the generator
    gen = get_db()
    # Get the session
    session = next(gen)
    assert session is not None
    # Close it (simulated by generator exit)
    try:
        next(gen)
    except StopIteration:
        pass
    session.close()
