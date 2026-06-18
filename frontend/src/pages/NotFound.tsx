import { useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const NotFound = () => {
  const location = useLocation();

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-4">
        <h1 className="text-6xl font-bold gradient-text">404</h1>
        <p className="text-xl text-muted-foreground">Page not found</p>
        <p className="text-sm text-muted-foreground">
          The route <code className="text-foreground">{location.pathname}</code> does not exist.
        </p>
        <Button asChild>
          <Link to="/">Back to Chat</Link>
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
