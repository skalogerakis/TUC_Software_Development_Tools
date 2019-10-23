 #!/usr/bin/env bash

# colors
RED='\033[0;31m'
NC='\033[0m'

function sum_vector() {
    # Arguments:
    #     $1 vector
    # Returns:
    #     Sum of all vector elements

    sum=0
    local -n _vector=$1
    for i in "${_vector[@]}"; do
        sum=`echo "scale=9; $sum + $i" | bc `
    done
    echo $sum
}

function sum_vector_pow2() {
    # Arguments:
    #     $1 vector
    # Returns:
    #     Sum(vector[i]^2) for i in len(vector x)
    
    sum=0
    local -n _vector=$1
    for i in "${_vector[@]}"; do
        sum=`echo "scale=9; $sum + ($i^2)" | bc `
    done
    echo $sum
}

function sum_vextor_vector() {
    # Arguments:
    #     $1 vector x
    #     $2 vector y
    #
    #     Vectors must be same size        
    # Returns:
    #     Sum(X[i]*Y[i]) for i in len(vector x)

    local -n _vector_X=$1
    local -n _vector_Y=$2
    len=$((${#_vector_X[@]} - 1))

    sum=0
    for i in $(seq 0 $len); do
        sum=`echo "scale=9; $sum + ( ${_vector_X[$i]}* ${_vector_Y[$i]})" | bc`
    done
    echo $sum
}

function regr() {
    # Arguments:
    #     $1 vector x
    #     $2 vector y
    #
    #     Vectors must be same size        
    # Returns:
    #     a b c err 

    local -n _Vector_X=$1
    local -n _Vector_Y=$2

    length=${#_Vector_X[@]}
    sum_xy=`sum_vextor_vector _Vector_X Vector_Y`
    sum_x=`sum_vector _Vector_X`
    sum_y=`sum_vector Vector_Y`
    sum_x2=`sum_vector_pow2 _Vector_X`

    # regular expresion for sed
    sed_regex='s|^(-*)\.|\10.|;s|([0-9]+\.[0-9]{2})[0-9]*|\1|;s|(\.[0-9])$|\10|;s|\.0{2}||'

    # calculate a
    a_num=`echo "scale=9; ($length * $sum_xy) - ($sum_x * $sum_y)" | bc`
    a_denom=`echo "scale=9; ( $length * $sum_x2 ) - ($sum_x * $sum_x)" | bc`

    # check for division by zero
    if [[ $a_denom == '0' ]]; then
        echo $RED "\bError: Incorrect vector" $NC
        return 1
    fi

    a=`echo "scale=2; $a_num / $a_denom" | bc | sed -r $sed_regex`

    # calculate b
    b=`echo "scale=2; ($sum_y - ($a * $sum_x)) / ($length)" | bc | sed -r $sed_regex`
    
    # c is always 1
    c=1

    # len = length of vector - 1 for loop
    len=$((${#Vector_X[@]} - 1))
    
    # calculate error
    err=0
    for i in $(seq 0 $len); do
        err=`echo "scale=2; $err + (${Vector_Y[$i]} - ( $a * (${_Vector_X[$i]}) + $b))^2" | bc | sed -r $sed_regex`
    done

    # echo "a=" $a "b=" $b "c=" $c
    printf "a=%s b=%s c=%s err=%s" $a $b $c $err
}

function regr_file() {
    # Arguments:
    #     $1 filename

    file=$1

    # Check if file exists and is readable
    if [[ ! -r $file ]]; then
        echo $RED "\bError: File not found, ensure file exists and is readable" $NC
        return 1
    fi    
    
    Vector_X=()
    Vector_Y=()
    counter=0

    # Set IFS to none, so no splitting of line
    # [[ -n $line ]] prevents the last line from being ignored if it doesn't end with a \n 
    while IFS='' read -r line || [[ -n "$line" ]]; do
        # Split line
        arrLine=(${line//:/ })

        # Check if values are numbers
        regex='^[0-9]+(\.[0-9]+)?$'
        if ! [[ ${arrLine[0]} =~ $regex ]] || ! [[ ${arrLine[1]} =~ $regex ]] ; then
            printf "%s%s:%s:Input file syntax error%s"   $RED $file $counter $NC
            return 1
        fi
        
        # Append values to vectors
        Vector_X+=(${arrLine[0]})
        Vector_Y+=(${arrLine[1]})
    done < "$file"

    regr Vector_X Vector_Y
}

for file in "$@"
do
    echo -e "FILE:" $file '\b,' `regr_file $file`
done