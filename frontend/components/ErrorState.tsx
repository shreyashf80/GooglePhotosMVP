import Icon from "./Icon";
export default function ErrorState({ message = "Something went wrong. Try again.", retry }: { message?: string; retry: () => void }) {
  return <div className="error-state" role="alert"><Icon name="cloud_off" size={36} /><p>{message}</p><button className="text-button" onClick={retry}>Try again</button></div>;
}
