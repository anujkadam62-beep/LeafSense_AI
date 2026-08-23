import { Sidebar } from "@/components/Sidebar";

export default function DashboardGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-full w-full">
      <Sidebar />
      <div className="flex min-h-full flex-1 flex-col">{children}</div>
    </div>
  );
}
