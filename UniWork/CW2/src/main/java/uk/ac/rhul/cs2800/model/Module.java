package uk.ac.rhul.cs2800.model;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a module with a unique code, name, and mandatory status.
 */
@Entity
public class Module {

  /**
   * The unique identifier for the module.
   */
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  /**
   * The module code, which uniquely identifies the module.
   */
  @Column(unique = true, nullable = false, length = 10)
  private String code;

  /**
   * The name of the module.
   */
  @Column(length = 100, nullable = false)
  private String name;

  /**
   * shows whether the module is mandatory.
   */
  private boolean mandatory;

  /**
   * List of registrations for this module.
   */
  @OneToMany(mappedBy = "module", cascade = CascadeType.ALL, orphanRemoval = true)
  private List<Registration> registrations = new ArrayList<>();

  /**
   * Default constructor for JPA.
   */
  public Module() {}

  /**
   * Constructs a new module.
   *
   * @param code      the module code.
   * @param name      the module name.
   * @param mandatory whether the module is mandatory.
   */
  public Module(String code, String name, boolean mandatory) {
    this.code = code;
    this.name = name;
    this.mandatory = mandatory;
  }

  /**
   * Returns the unique identifier for the module.
   *
   * @return the id.
   */
  public Long getId() {
    return id;
  }

  /**
   * Returns the module code.
   *
   * @return the code.
   */
  public String getCode() {
    return code;
  }

  /**
   * Returns the module name.
   *
   * @return the name
   */
  public String getName() {
    return name;
  }

  /**
   * Returns whether the module is mandatory.
   *
   * @return true if the module is mandatory false otherwise
   */
  public boolean isMandatory() {
    return mandatory;
  }

  /**
   * Returns the list of registrations for the module.
   *
   * @return the list of registrations
   */
  public List<Registration> getRegistrations() {
    return registrations;
  }
}
