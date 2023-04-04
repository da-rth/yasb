import { DomSanitizer } from "@angular/platform-browser";
import { PipeTransform, Pipe } from "@angular/core";

@Pipe({ name: "safeHtml" })
export class SafeHtmlPipe implements PipeTransform {
    constructor(private sanitized: DomSanitizer) {}
    transform(value?: string) {
        return value ? this.sanitized.bypassSecurityTrustHtml(value) : "";
    }
}
