package uk.ac.rhul.cs2800.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import uk.ac.rhul.cs2800.model.Grade;
import uk.ac.rhul.cs2800.model.Module;
import uk.ac.rhul.cs2800.model.Student;
import uk.ac.rhul.cs2800.repository.GradeRepository;
import uk.ac.rhul.cs2800.repository.ModuleRepository;
import uk.ac.rhul.cs2800.repository.StudentRepository;

import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Test class for the GradeController.
 */
@SpringBootTest
@AutoConfigureMockMvc
public class GradeControllerTest {

  @Autowired
  private MockMvc mockMvc;

  @Autowired
  private ObjectMapper objectMapper;

  @Autowired
  private GradeRepository gradeRepository;

  @Autowired
  private StudentRepository studentRepository;

  @Autowired
  private ModuleRepository moduleRepository;

  /**
   * Sets up test data before each test to ensure a clean state.
   */
  @BeforeEach
  public void setup() {
    // Clear the database to avoid duplicate entries or residual data
    gradeRepository.deleteAll();
    studentRepository.deleteAll();
    moduleRepository.deleteAll();

    // Insert test data for a student and a module
    studentRepository.save(new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk"));
    moduleRepository.save(new Module("CS101", "Introduction to Computer Science", true));
  }

  /**
   * Test for adding a valid grade via the /grades/addGrade endpoint.
   *
   * @throws Exception if the request or assertions fail
   */
  @Test
  public void addGradeTest() throws Exception {
    // Setup test data
    Long studentId = 1L;
    String moduleCode = "CS101";

    Map<String, String> params = new HashMap<>();
    params.put("student_id", String.valueOf(studentId));
    params.put("module_code", moduleCode);
    params.put("score", "85");

    // Execute the POST request
    MvcResult result = mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isOk())
        .andReturn();

    // Validate response and database state
    Grade savedGrade = objectMapper.readValue(
        result.getResponse().getContentAsString(), Grade.class);
    assertThat(savedGrade).isNotNull();
    assertThat(savedGrade.getScore()).isEqualTo(85);
    assertThat(savedGrade.getStudent().getId()).isEqualTo(studentId);
    assertThat(savedGrade.getModule().getCode()).isEqualTo(moduleCode);
  }

  /**
   * Test for attempting to add a grade with missing parameters.
   *
   * @throws Exception if the request fails
   */
  @Test
  public void addGradeWithMissingParams() throws Exception {
    Map<String, String> params = new HashMap<>();
    params.put("student_id", "1"); // Missing module_code and score

    mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isBadRequest());
  }

  /**
   * Test for attempting to add a grade for a non-existent student.
   *
   * @throws Exception if the request fails
   */
  @Test
  public void addGradeForNonExistentStudent() throws Exception {
    Map<String, String> params = new HashMap<>();
    params.put("student_id", "999"); // Non-existent student ID
    params.put("module_code", "CS101");
    params.put("score", "85");

    mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isBadRequest());
  }

  /**
   * Test for attempting to add a grade for a non-existent module.
   *
   * @throws Exception if the request fails
   */
  @Test
  public void addGradeForNonExistentModule() throws Exception {
    Map<String, String> params = new HashMap<>();
    params.put("student_id", "1");
    params.put("module_code", "NON_EXISTENT"); // Non-existent module code
    params.put("score", "85");

    mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isBadRequest());
  }

  /**
   * Test for adding a grade with an invalid score.
   *
   * @throws Exception if the request fails
   */
  @Test
  public void addGradeWithInvalidScore() throws Exception {
    Map<String, String> params = new HashMap<>();
    params.put("student_id", "1");
    params.put("module_code", "CS101");
    params.put("score", "-10"); // Invalid score

    mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isBadRequest());
  }

  /**
   * Test for adding a grade with non-numeric score value.
   *
   * @throws Exception if the request fails
   */
  @Test
  public void addGradeWithNonNumericScore() throws Exception {
    Map<String, String> params = new HashMap<>();
    params.put("student_id", "1");
    params.put("module_code", "CS101");
    params.put("score", "eighty-five"); // Non-numeric score

    mockMvc.perform(MockMvcRequestBuilders.post("/grades/addGrade")
            .contentType(MediaType.APPLICATION_JSON)
            .content(objectMapper.writeValueAsString(params)))
        .andExpect(status().isBadRequest());
  }
}
