import Input from "../components/common/Input.tsx";
import {SubmitHandler, useForm} from "react-hook-form"

interface IFormValues {
    Name:string,
    Email?:string,
    Password:string,
    phone:string,
    Link:string,
    price:number
}

const InputDemo = () => {
    const {
        register,
        handleSubmit,
        formState: {errors},
    } = useForm();

    const onSubmit: SubmitHandler<IFormValues> = (data) => {
        alert(JSON.stringify(data))
    }

    return (
        <div className="text-center w-1/4 mx-auto dark:bg-gray-500 bg-gray-100 p-1 rounded-2xl">
            <label htmlFor="form_1" className="text-4xl mb-6 py-4">Input Demo</label>
            <form
                className="pt-4"
                id="form_1"
                onSubmit={handleSubmit(onSubmit)}>
                <Input
                    id="form_Name"
                    label="Name"
                    register={register}
                    required={true}
                    type="text"
                    placeholder="Type any thing"
                    error={errors["form_Name"]?errors["form_Name"].message:undefined}
                />
                <Input
                    id="form_Email"
                    label="Email"
                    register={register}
                    type="email"
                    placeholder="Type any email"
                    error={errors["form_Email"]?errors["form_Email"].message:undefined}
                />
                <Input
                    id="form_Password"
                    label="password"
                    register={register}
                    required
                    type="password"
                    placeholder="Type any math"
                    error={errors["form_Password"]?errors["form_Password"].message:undefined}
                />
                <Input
                    id="form_phone"
                    label="phone"
                    register={register}
                    required
                    type="tel"
                    placeholder="Type any math"
                    error={errors["form_phone"]?errors["form_phone"].message:undefined}
                    />
                <Input
                    id="form_link"
                    label="Link"
                    register={register}
                    required
                    type="url"
                    placeholder="Type any math"
                    className="w-full"
                    error={errors["form_link"]?errors["form_link"].message:undefined}
                />
                <Input
                    id="form_price"
                    label="price"
                    register={register}
                    required
                    type="number"
                    placeholder="Type any math"
                    error={errors["form_price"]?errors["form_price"].message:undefined}
                />

                <Input id="Btn-Submit" register={register} type="submit" value="Submit" />
                    </form>
        </div>
    );
}

export default InputDemo;