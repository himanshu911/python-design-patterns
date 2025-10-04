from singleton.classic_singleton import Singleton


def test_singleton_same_instance():
    """Test that multiple instantiations return the same object."""
    instance1 = Singleton()
    instance2 = Singleton()
    assert instance1 is instance2


def test_singleton_id_check():
    """Test that instances have the same memory address."""
    instance1 = Singleton()
    instance2 = Singleton()
    assert id(instance1) == id(instance2)


def test_singleton_multiple_calls():
    """Test that calling Singleton() multiple times returns same instance."""
    instances = [Singleton() for _ in range(10)]

    # All instances should be the same object
    first = instances[0]
    for instance in instances[1:]:
        assert instance is first
