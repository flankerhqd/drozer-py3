import android.content.pm.PackageManager;
import android.content.pm.PermissionInfo;
import android.content.pm.PermissionGroupInfo;
import org.json.JSONArray;
import org.json.JSONObject;

class PermissionHelper{
    public static String all(PackageManager pm) {
        try {
            JSONArray jsonArray = new JSONArray();
            for (PermissionInfo info : pm.queryPermissionsByGroup(null, 0)) {
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("packageName", info.packageName);
                jsonObject.put("name", info.name);
                jsonObject.put("protectionLevel", info.protectionLevel);
                jsonArray.put(jsonObject);
            }
            // append all groups except `null` group
            for (PermissionGroupInfo groupInfo : pm.getAllPermissionGroups(0)) {
                for (PermissionInfo info : pm.queryPermissionsByGroup(groupInfo.name, 0)) {
                    JSONObject jsonObject = new JSONObject();
                    jsonObject.put("packageName", info.packageName);
                    jsonObject.put("name", info.name);
                    jsonObject.put("protectionLevel", info.protectionLevel);
                    jsonArray.put(jsonObject);
                }
            }
            return jsonArray.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }
    public static String single(PackageManager pm, String permission) {
        try {
            PermissionInfo info = pm.getPermissionInfo(permission , 0);
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("packageName", info.packageName);
            jsonObject.put("name", info.name);
            jsonObject.put("protectionLevel", info.protectionLevel);
            return jsonObject.toString();
        } catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }
}
