import android.content.pm.PackageManager;
import android.content.pm.PermissionInfo;
import org.json.JSONArray;
import org.json.JSONObject;

class PermissionHelper{
    public static String query(PackageManager pm, String permissionGroup, int flags) {
        try {
            JSONArray jsonArray = new JSONArray();
            for (PermissionInfo info : pm.queryPermissionsByGroup(null, 0)) {
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("packageName", info.packageName);
                jsonObject.put("name", info.name);
                jsonObject.put("protectionLevel", info.protectionLevel);
                jsonArray.put(jsonObject);
            }
            return jsonArray.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }
}
