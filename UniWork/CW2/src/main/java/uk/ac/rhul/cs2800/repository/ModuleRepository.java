package uk.ac.rhul.cs2800.repository;

import java.util.Optional;
import org.springframework.data.repository.CrudRepository;
import uk.ac.rhul.cs2800.model.Module;

/**
 * Repository for Module entities.
 */
public interface ModuleRepository extends CrudRepository<Module, Long> {

  /**
   * Find a Module by its code.
   *
   * @param code the code of the Module.
   * @return an Optional containing the Module if found, or empty otherwise.
   */
  Optional<Module> findByCode(String code);
}
