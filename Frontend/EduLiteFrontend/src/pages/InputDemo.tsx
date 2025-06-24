import Input from "../components/common/Input";
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
        reset,
        formState: {errors},
    } = useForm();

    const onSubmit: SubmitHandler<IFormValues> = (data) => {
        confirm(JSON.stringify(data))?reset():null
    }

    return (
        <div className="text-center w-1/4 mx-auto dark:bg-gray-500 bg-gray-100 p-1 rounded-2xl">
            <label htmlFor="form_1" className="text-4xl mb-6 py-4">Input Demo</label>
            <form
                className="pt-4"
                id="form_1"
                onSubmit={handleSubmit(onSubmit)}
                onReset={()=>{reset()}}>
                <Input id={"s"} register={register}/>
                <Input
                    id="form_Name"
                    label="Name"
                    register={register}
                    required={true}
                    type="text"
                    placeholder="Type any thing"
                    hint="*type your name"
                    disablePaste={true}
                    maxLength={50}
                    minLength={5}
                    error={errors["Name"]?errors["Name"].message.toString():undefined}
                />
                <Input
                    id="form_Email"
                    label="Email"
                    register={register}
                    type="email"
                    placeholder="Type any email"
                    error={errors["Email"]?errors["Email"].message.toString():undefined}
                />
                <Input
                    id="form_Password"
                    label="password"
                    register={register}
                    required
                    type="password"
                    placeholder="Type any math"
                    error={errors["password"]?errors["password"].message.toString():undefined}
                />
                <Input
                    id="form_phone"
                    label="phone"
                    register={register}
                    required
                    type="tel"
                    placeholder="Type any math"
                    error={errors["phone"]?errors["phone"].message.toString():undefined}
                    />
                <Input
                    id="form_link"
                    label="Link"
                    register={register}
                    required
                    type="url"
                    placeholder="Type any math"
                    className="w-full"
                    error={errors["Link"]?errors["Link"].message.toString():undefined}
                />
                <Input
                    id="form_price"
                    label="price"
                    register={register}
                    required
                    minValue={20}
                    maxValue={50}
                    type="number"
                    placeholder="Type any math"
                    error={errors["price"]?errors["price"].message.toString():undefined}
                />
                <Input
                    id={"form_date"}
                    register={register}
                    type="date"
                    error={errors["form_date"]?errors["form_date"].message.toString():undefined}
                    />
                <Input id="Btn-Submit" register={register} type="submit" value="Submit" />
                <Input id="Btn-Reset" register={register} type="reset" value="Reset" />
                    </form>
        </div>
    );
}

export default InputDemo;