/**
 * Reusable Input component for EduLite, styled with Tailwind CSS , controlled with React-Hook-Form.
 *
 * Props:
 * - id: make every input unique.
 * - label?: label for Input
 * - type?: 'password' | 'text' | 'email' | 'number' | 'tel' | 'url'  (visual style)
 * - register: function of react-hook-form
 * - disabled?: If true, Input is disabled
 * - className?: Additional Tailwind classes
 * - error?: For any Error in user Inputs
 * - required?: if true , Input is required
 * - placeholder?: placeholder For Input
 * - value?: value for Input
 * - minValue?: min value for number Input
 * - maxValue?: max value for number Input
 * - minLength?: min number of character
 * - maxLength?: max number of character
 * - disablePaste?: If true, disable Paste action
 * - hint?: message for hint
 * - onChangeHandle?: Handle Input Changes

 *
 * Usage examples:
 * <Input id={"s"} register={register}/>
 * <Input
 *   id="form_Name"
 *   label="Name"
 *   register={register}
 *   required={true}
 *   type="text"
 *   placeholder="Type anything"
 *   hint="*type your name"
 *   disablePaste={true}
 *   maxLength={50}
 *   minLength={5}
 *   error={errors["Name"]?errors["Name"].message.toString():undefined}
 *   />
 * <Input
 *   id="form_price"
 *   label="price"
 *   register={register}
 *   required
 *   minValue={20}
 *   maxValue={50}
 *   type="number"
 *   placeholder="Type any math"
 *   error={errors["price"]?errors["price"].message.toString():undefined}
 *   />
 * <Input id="Btn-Reset" register={register} type="reset" value="Reset" />
 * <Input id="Btn-Submit" register={register} type="submit" value="Submit" />
 */
import * as React from "react";


type Props = {
    id: string;
    label?: string,
    register: Function,
    error?: string,
    required?: boolean,
    placeholder?: string,
    type?: 'password' | 'text' | 'email' | 'number' | 'tel' | 'url' | 'submit' | 'reset' | 'date',
    value?: string,
    onChangeHandle?: Function,
    className?: string,
    disabled?: boolean,
    disablePaste?: boolean,
    minLength?: number,
    maxLength?: number,
    minValue?: number,
    maxValue?: number,
    hint?: string,
}

const Input = (props:Props) =>{

    if (props.type === "submit" || props.type === "reset") {
        return (<input
            id={props.id}
            type={props.type}
            value={props.value}
            className={`block rounded-lg p-2.5 text-gray-50 mx-auto bg-gray-700 my-4 ${props.className || ""}`}
        />)
    }

    const stopPasteHandle = (e: React.ClipboardEvent<HTMLInputElement>)=>{
        e.preventDefault();
        alert("Paste is not Allow");
    }
    return (
        <div className="relative pt-4">

            <input {...props.register(props.label||props.id, {
                required: props.required?"this field is required ":false,
                minLength: props.minLength?{
  value:props.minLength,
  message:`Minimum Length is ${props.minLength}`,
  }:undefined,
                maxLength: props.maxLength?{
  value:props.maxLength,
  message:`Maximum Length is ${props.maxLength}`,
                }:undefined,
                min: props.minValue?{
  value:props.minValue,
  message:`Minimum Value is ${props.minValue}`,
                }:undefined,
                max: props.maxValue?{
     value:props.maxValue,
     message:`Maximum Value is ${props.maxValue}`,
 }:undefined,
            })}
 onPaste={props.disablePaste?(event)=>{stopPasteHandle(event)}:null}
 disabled={props.disabled}
 id={props.id}
 className={`block rounded-t-lg px-2.5 pb-2.5 pt-5 text-sm text-gray-900 bg-gray-50 dark:bg-gray-700 border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer ${props.className || ""}`}
 type={props.type || 'text'}
 placeholder={props.placeholder || 'Type any thing'}
 value={props.value}
 onChange={(e)=>{
     return props.onChangeHandle?props.onChangeHandle(e.target.value):()=>{}
 }}
            />
            {props.hint?<p role="document" className="text-sm text-black dark:text-white text-start">{props.hint}</p>:null}
            {props.error?<p role="alert" className="text-sm text-red-700 text-start">{props.error}</p>:null}
            <label htmlFor={props.id}
 className="absolute text-md peer-focus:text-lg text-gray-500 dark:text-gray-400 duration-300 transform -translate-y-4 scale-75 top-4 z-10 origin-[0] start-2.5 peer-focus:text-blue-600 peer-focus:font-bold peer-focus:dark:text-blue-500 peer-placeholder-shown:scale-100 peer-placeholder-shown:translate-y-0 peer-focus:scale-75 peer-focus:-translate-y-4 rtl:peer-focus:translate-x-1/4 rtl:peer-focus:left-auto">
                {props.label||""}</label>
        </div>
    )
}


export default Input;