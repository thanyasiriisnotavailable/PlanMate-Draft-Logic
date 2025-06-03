package senior.project.Controller;

import com.google.firebase.auth.FirebaseToken;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
public class UserProfileController {
    @GetMapping("/profile")
    public ResponseEntity<?> getProfile(HttpServletRequest request) {
        FirebaseToken user = (FirebaseToken) request.getAttribute("firebaseUser");

        if (user == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Unauthorized");
        }

        Map<String, String> profile = new HashMap<>();
        profile.put("email", user.getEmail());
        profile.put("uid", user.getUid());
        profile.put("name", user.getName());
        profile.put("image", user.getPicture());

        return ResponseEntity.ok(profile);
    }
}
