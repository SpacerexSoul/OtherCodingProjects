package uk.ac.rhul.cs2800.model;

/**
 * Exception thrown when no grade is available for a specific module.
 */
public class NoGradeAvailableException extends Exception {

  /**
   * Constructs a new NoGradeAvailableException with the given message.
   *
   * @param message the exception message.
   */
  public NoGradeAvailableException(String message) {
    super(message);
  }
}
