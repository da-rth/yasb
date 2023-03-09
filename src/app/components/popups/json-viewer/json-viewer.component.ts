import { CommonModule } from "@angular/common";
import {
  ChangeDetectorRef,
  Component,
  HostListener,
  OnDestroy,
  OnInit,
  ViewEncapsulation,
} from "@angular/core";
import { emit, listen, UnlistenFn } from "@tauri-apps/api/event";
import { appWindow } from "@tauri-apps/api/window";
import { NgxJsonViewerModule } from "ngx-json-viewer";
import { StylesWatcherComponent } from "../../styles-watcher.component";

@Component({
  standalone: true,
  selector: "json-viewer",
  templateUrl: "./json-viewer.component.html",
  styleUrls: ["./json-viewer.component.scss"],
  imports: [NgxJsonViewerModule, CommonModule],
  encapsulation: ViewEncapsulation.None,
})
export class JsonViewerComponent
  extends StylesWatcherComponent
  implements OnInit, OnDestroy
{
  public jsonData: any;
  private jsonDataUnlistenFn?: UnlistenFn;

  constructor(private cdr: ChangeDetectorRef) {
    super();
  }

  public async ngOnInit(): Promise<void> {
    super.ngOnInit();
    const dataEvent = `${appWindow.label}_data`;
    this.jsonDataUnlistenFn = await listen(dataEvent, async (event) => {
      await appWindow.show().then(async () => {
        this.jsonData = event.payload;
        this.cdr.detectChanges();
        if (!this.jsonData) {
          await appWindow.hide();
        }
      });
    });
    await emit(`${appWindow.label}_init`);
  }

  public async ngOnDestroy(): Promise<void> {
    await super.ngOnDestroy();
    this.jsonDataUnlistenFn && this.jsonDataUnlistenFn();
  }

  @HostListener("document:keydown.escape")
  protected async onEscape(): Promise<void> {
    await appWindow.hide();
  }
}
