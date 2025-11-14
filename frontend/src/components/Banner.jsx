//import Logo from "../assets/logo.svg";  need to get the logo svg later
const Logo = null;

const Banner = () => {
  return (
    <div className="w-full h-32 bg-yellow-400 flex justify-center items-center shadow-md">
        {Logo ? (
            <img src={Logo} alt="Logo" className="h-20" />
        ) : (
            <span className="text-white text-7xl font-bold">Company</span> //for anonymity
        )}
    </div>
  );
};

export default Banner;