package uk.ac.rhul.cs2800.model;

/**
 * Represents a grade given to a student for a specific module.
 */
public class Grade {
  private int score;
  private Module module;

  /**
   * Constructor for a new Grade.
   *
   * @param score  the score of the grade.
   * @param module the module associated with this grade.
   */
  public Grade(int score, Module module) {
    this.score = score;
    this.module = module;
  }

  /**
   * Returns the score of the grade.
   *
   * @return the score.
   */
  public int getScore() {
    return score;
  }

  /**
   * Returns the module associated with this grade.
   *
   * @return the module.
   */
  public Module getModule() {
    return module;
  }
}
