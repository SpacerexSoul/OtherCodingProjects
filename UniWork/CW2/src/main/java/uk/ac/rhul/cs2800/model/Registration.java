package uk.ac.rhul.cs2800.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;

/**
 * Represents a registration of a student to a module.
 */
@Entity
public class Registration {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @ManyToOne
  @JoinColumn(name = "student_id", nullable = false)
  private Student student;

  @ManyToOne
  @JoinColumn(name = "module_code", nullable = false)
  private Module module;

  /**
   * Default constructor for JPA.
   */
  public Registration() {}

  /**
   * Creates a new registration linking a student to a module.
   *
   * @param student the student
   * @param module the module
   */
  public Registration(Student student, Module module) {
    this.student = student;
    this.module = module;
  }

  public Long getId() {
    return id;
  }

  public Student getStudent() {
    return student;
  }

  public void setStudent(Student student) {
    this.student = student;
  }

  public Module getModule() {
    return module;
  }

  public void setModule(Module module) {
    this.module = module;
  }
}
