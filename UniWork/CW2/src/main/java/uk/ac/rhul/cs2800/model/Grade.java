package uk.ac.rhul.cs2800.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;

/**
 * Represents a grade given to a student for a specific module.
 */
@Entity
public class Grade {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  /**
   * The score of the grade.
   */
  private int score;

  /**
   * The module associated with this grade.
   */
  @ManyToOne
  @JoinColumn(name = "module_code", nullable = false)
  private Module module;

  /**
   * The student who received this grade.
   */
  @ManyToOne
  @JoinColumn(name = "student_id", nullable = false)
  private Student student;

  /**
   * Default constructor for JPA.
   */
  public Grade() {}

  /**
   * Constructor for a new Grade with a score and a module.
   *
   * @param score  the score of the grade.
   * @param module the module associated with this grade.
   */
  public Grade(int score, Module module) {
    this.score = score;
    this.module = module;
  }

  /**
   * Constructor for a new Grade with a score, module, and student.
   *
   * @param score   the score of the grade.
   * @param module  the module associated with this grade.
   * @param student the student associated with this grade.
   */
  public Grade(int score, Module module, Student student) {
    this.score = score;
    this.module = module;
    this.student = student;
  }

  /**
   * Returns the ID of the grade.
   *
   * @return the id
   */
  public Long getId() {
    return id;
  }

  /**
   * Sets the score of the grade.
   *
   * @param score the new score
   */
  public void setScore(int score) {
    this.score = score;
  }

  /**
   * Returns the score of the grade.
   *
   * @return the score
   */
  public int getScore() {
    return score;
  }

  /**
   * Returns the module associated with this grade.
   *
   * @return the module
   */
  public Module getModule() {
    return module;
  }

  /**
   * Sets the module associated with this grade.
   *
   * @param module the module
   */
  public void setModule(Module module) {
    this.module = module;
  }

  /**
   * Returns the student associated with this grade.
   *
   * @return the student
   */
  public Student getStudent() {
    return student;
  }

  /**
   * Sets the student associated with this grade.
   *
   * @param student the student
   */
  public void setStudent(Student student) {
    this.student = student;
  }
}
