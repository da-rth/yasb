import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";
import { AppModule } from "./app/app.module";

platformBrowserDynamic()
    .bootstrapModule(AppModule, {
        preserveWhitespaces: false,
    })
    .catch((err) => console.error(err));
