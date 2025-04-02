package uk.ac.rhul.cs2800.model;

/**
 * Exception thrown when attempting to access grades for unregistered modules.
 */
public class NoRegistrationException extends Exception {

  /**
   * Constructs a new NoRegistrationException with the given message.
   *
   * @param message the exception message
   */
  public NoRegistrationException(String message) {
    super(message);
  }
}
