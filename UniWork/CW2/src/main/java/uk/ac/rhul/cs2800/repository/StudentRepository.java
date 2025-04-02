package uk.ac.rhul.cs2800.repository;

import org.springframework.data.repository.CrudRepository;
import uk.ac.rhul.cs2800.model.Student;

/**
 * A repository that manages Student instances.
 */
public interface StudentRepository extends CrudRepository<Student, Long> {

}
