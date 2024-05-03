import type { Author } from "../../js/interfaces";

let user = $state(null);
let shown = $state(false);

export function getViewUserState() {
    function setUser(newUser: Author | null) {
        if (newUser === user) {
            return;
        }
        if (!newUser) {
            shown = false;
            console.log("viewUserState - hidden user");
        }
        user = newUser;
        if (user) {
            shown = true;
            console.log("viewUserState - shown user", user);
        }
    }
    return {
        get user() {
            return user;
        },
        get shown() {
            return shown;
        },
        setUser,
    };
}

