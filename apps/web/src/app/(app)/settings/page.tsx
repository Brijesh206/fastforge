import { redirect } from "next/navigation";

/** /settings has no content of its own — General is the landing tab. */
export default function SettingsIndexPage() {
  redirect("/settings/general");
}
