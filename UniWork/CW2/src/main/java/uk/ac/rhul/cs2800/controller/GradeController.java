package uk.ac.rhul.cs2800.controller;

import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import uk.ac.rhul.cs2800.model.Grade;
import uk.ac.rhul.cs2800.model.Module;
import uk.ac.rhul.cs2800.model.Student;
import uk.ac.rhul.cs2800.repository.GradeRepository;
import uk.ac.rhul.cs2800.repository.ModuleRepository;
import uk.ac.rhul.cs2800.repository.StudentRepository;

/**
 * Controller for handling Grade operations.
 */
@RestController
public class GradeController {

  private final GradeRepository gradeRepository;
  private final StudentRepository studentRepository;
  private final ModuleRepository moduleRepository;

  /**
   * Constructor for dependency injection.
   *
   * @param gradeRepository the repository for Grade objects.
   * @param studentRepository the repository for Student objects.
   * @param moduleRepository the repository for Module objects.
   */
  public GradeController(GradeRepository gradeRepository, StudentRepository studentRepository,
                         ModuleRepository moduleRepository) {
    this.gradeRepository = gradeRepository;
    this.studentRepository = studentRepository;
    this.moduleRepository = moduleRepository;
  }

  /**
   * Handles POST requests to add a new Grade.
   *
   * @param params a map containing the student ID, module code, and grade score.
   * @return a ResponseEntity containing the saved Grade object or a bad request status.
   */
  @PostMapping(value = "/grades/addGrade")
  public ResponseEntity<Grade> addGrade(@RequestBody Map<String, String> params) {
    try {
      Long studentId = Long.parseLong(params.get("student_id"));
      String moduleCode = params.get("module_code");
      int score = Integer.parseInt(params.get("score"));

      // find the student and module
      Student student = studentRepository.findById(studentId)
          .orElseThrow(() -> new IllegalArgumentException("Student not found"));
      Module module = moduleRepository.findByCode(moduleCode)
          .orElseThrow(() -> new IllegalArgumentException("Module not found"));

      // create and save the grade
      Grade grade = new Grade(score, module, student);
      Grade savedGrade = gradeRepository.save(grade);

      return ResponseEntity.ok(savedGrade);
    } catch (NumberFormatException e) {
      return ResponseEntity.badRequest().body(null); // Handle invalid input formats
    } catch (IllegalArgumentException e) {
      return ResponseEntity.badRequest().body(null); // Handle missing entities
    } catch (Exception e) {
      return ResponseEntity.internalServerError().body(null); // Handle unexpected errors
    }
  }
}
